#!/usr/bin/env python3

import sqlite3
from datetime import datetime
from enum import Enum
from typing import Mapping, Optional

from grantme.constants.msgs import *
from grantme.constants.sqls import *
from grantme.utils.errors import *

from .utils import printers, timer


# explicit replacements of the default adapter/converter deprecated in Python 3.12;
# a fixed format keeps stored timestamps comparable as strings
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
sqlite3.register_adapter(datetime, lambda dt: dt.strftime(TIMESTAMP_FORMAT))
sqlite3.register_converter(
    "timestamp", lambda b: datetime.strptime(b.decode(), TIMESTAMP_FORMAT)
)


class Mode(Enum):
    EXCLUSIVE = 1
    SHARED = 2


class LockStatus:
    def __init__(self, mode: Mode, user_expires: Mapping[str, datetime]):
        self.mode = mode
        self.user_expires = user_expires


class GrantResult:
    def __init__(
        self,
        curr_mode: Optional[Mode],
        prev_mode: Optional[Mode],
        curr_expire_at: Optional[datetime],
        prev_expire_at: Optional[datetime],
    ):
        self.curr_mode = curr_mode
        self.prev_mode = prev_mode
        self.curr_expire_at = curr_expire_at
        self.prev_expire_at = prev_expire_at


def write_lock(who: str, mode: Mode, expire_at: datetime, conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        UPSERT,
        {"who": who, "shared": mode == Mode.SHARED, "expire_at": expire_at},
    )
    assert cur.rowcount == 1
    cur.close()


def get_status(conn: sqlite3.Connection) -> Optional[LockStatus]:
    now = datetime.now()

    cur = conn.cursor()
    cur.execute(QUERY_SHARED, {"now": now})
    rows = cur.fetchall()
    if len(rows) > 0:
        cur.close()
        return LockStatus(
            mode=Mode.SHARED,
            user_expires={row["user"]: row["expire_at"] for row in rows},
        )

    cur.execute(QUERY_EXCLUSIVE, {"now": now})
    row = cur.fetchone()
    if row is not None:
        cur.close()
        return LockStatus(
            mode=Mode.EXCLUSIVE, user_expires={row["user"]: row["expire_at"]}
        )

    cur.close()
    return None


def revoke(who, conn: sqlite3.Connection) -> Optional[Mode]:
    status = get_status(conn)

    if status is None:
        return None

    if who not in status.user_expires:
        return None

    cur = conn.cursor()
    cur.execute(RELEASE, {"who": who})
    assert cur.rowcount == 1
    cur.close()
    conn.commit()

    return status.mode


def grant(
    who: str, wanted: Mode, duration: str, conn: sqlite3.Connection
) -> GrantResult:
    attempted_expire = datetime.now() + timer.parse_delta(duration)

    status = get_status(conn)
    result = GrantResult(None, None, None, None)

    # Case 1: if no lock is granted, simply grant one
    if status is None:
        write_lock(who, wanted, attempted_expire, conn)
        conn.commit()

        result.curr_mode = wanted
        result.curr_expire_at = attempted_expire
        return result

    # Case 2: if neither s- nor x-locked, try lock
    if who not in status.user_expires:
        # cannot want shared when an exclusive is granted (not to `who`)
        # cannot want exclusive when any other lock is granted (not to `who`)
        if (wanted == Mode.SHARED and status.mode == Mode.EXCLUSIVE) or (
            wanted == Mode.EXCLUSIVE and len(status.user_expires) > 0
        ):
            raise GrantmeError(
                GRANT_FAILURE_MSG.format(
                    wanted=wanted.name.lower(),
                    mode=status.mode.name.lower(),
                    holders=printers.format_holders(status.user_expires),
                ),
                GRANT_FAILURE_CODE,
            )

        write_lock(who, wanted, attempted_expire, conn)
        conn.commit()

        result.curr_mode = wanted
        result.curr_expire_at = attempted_expire
        return result

    # Case 3: if already locked, try (upgrade and) prolong
    result.prev_mode = status.mode

    # prevent accidental downgrade
    if result.prev_mode == Mode.EXCLUSIVE and wanted == Mode.SHARED:
        wanted = Mode.EXCLUSIVE

    # try upgrade
    if result.prev_mode == Mode.SHARED and wanted == Mode.EXCLUSIVE:
        if len(status.user_expires) > 1:
            others = {
                user: expire_at
                for user, expire_at in status.user_expires.items()
                if user != who
            }
            raise GrantmeError(
                UPGRADE_FAILURE_MSG.format(holders=printers.format_holders(others)),
                UPGRADE_FAILURE_CODE,
            )

        cur = conn.cursor()
        cur.execute(UPGRADE, {"who": who})
        assert cur.rowcount == 1
        cur.close()

        result.curr_mode = Mode.EXCLUSIVE
    else:
        result.curr_mode = result.prev_mode

    # try prolong
    old_expire = status.user_expires[who]
    result.prev_expire_at = old_expire
    if old_expire > attempted_expire:
        result.curr_expire_at = old_expire
    else:
        write_lock(who, wanted, attempted_expire, conn)
        result.curr_expire_at = attempted_expire

    conn.commit()
    return result


def list_users(conn: sqlite3.Connection):
    status = get_status(conn)
    if status is None:
        return

    print(", ".join(status.user_expires.keys()))
    print(max(status.user_expires.values()))


def print_status(you: str, conn: sqlite3.Connection):
    status = get_status(conn)

    printers.show_sep_line()

    if status is None:
        printers.show_free()
    else:
        exclusive = status.mode == Mode.EXCLUSIVE
        printers.show_holders(exclusive, status.user_expires, you)
        if you not in status.user_expires:
            if exclusive:
                printers.warning(DO_NOT_DISTURB)
            else:
                printers.slock_guide()

    printers.show_sep_line()


def revoke_and_print_result(who, conn: sqlite3.Connection):
    result = revoke(who, conn)
    if result is None:
        printers.warning(NOTHING_REVOKED.format(who=who))
    else:
        printers.ok(REVOKE_OK.format(who=who, mode=result.name.lower()))


def grant_and_print_result(
    who: str, want_shared: bool, duration: str, conn: sqlite3.Connection
):
    result = grant(who, Mode.SHARED if want_shared else Mode.EXCLUSIVE, duration, conn)
    assert result.curr_mode is not None
    assert result.curr_expire_at is not None

    fields = {
        "who": who,
        "mode": result.curr_mode.name.lower(),
        "until": printers.format_until(result.curr_expire_at, highlight=False),
    }

    # when called without a lock already held
    if result.prev_mode is None:
        printers.ok(GRANT_OK.format(**fields))
        return

    # when called with a lock already held
    if result.prev_mode == Mode.EXCLUSIVE and want_shared:
        printers.warning(ATTEMPT_SLOCK_WITH_XLOCK.format(**fields))

    if result.prev_mode == Mode.SHARED and result.curr_mode == Mode.EXCLUSIVE:
        printers.ok(UPGRADE_OK.format(**fields))
    elif result.prev_expire_at == result.curr_expire_at:
        printers.warning(ATTEMPT_SHORTER_DURATION_THAN_ALREADY_GRANTED.format(**fields))
    else:
        printers.ok(PROLONG_OK.format(**fields))
