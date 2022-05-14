#!/usr/bin/env python3

import sqlite3
from datetime import datetime
from os.path import join
from pathlib import Path

from . import defs
from .utils import errors, printers, timer


def setup(dir: str, db_filename: str):
    Path.mkdir(dir, parents=True, exist_ok=True)
    conn = sqlite3.connect(join(dir, db_filename))
    setup_db(conn)


def setup_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(defs.SQL.CREATE_DB)
    cur.execute(defs.SQL.CREATE_INDEX)
    cur.close()
    conn.commit()


def write_expire(who: str, shared: bool, expire_at: datetime, conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(defs.SQL.UPSERT, {"who": who, "shared": shared, "expire_at": expire_at})
    assert cur.rowcount == 1
    cur.close()


def granted(conn: sqlite3.Connection):
    now = datetime.now()

    cur = conn.cursor()
    cur.execute(defs.SQL.QUERY_SHARED, {"now": now})
    rows = cur.fetchall()
    shares = {row["user"]: row["expire_at"] for row in rows}

    cur.execute(defs.SQL.QUERY_EXCLUSIVE, {"now": now})
    row = cur.fetchone()
    if row is not None:
        exclusive = (row["user"], row["expire_at"])
    else:
        exclusive = None

    cur.close()
    return shares, exclusive


def print_status(you: str, conn: sqlite3.Connection):
    print()
    printers.show_sep_line()

    shares, exclusive = granted(conn)

    if exclusive is not None:
        who, expire = exclusive
        if who == you:
            who += " (YOU)"
            printers.show_granted("Exclusive", expire, highlighted_user=who)
        else:
            printers.show_granted("Exclusive", expire, others=[who])
            printers.warning(defs.Message.DO_NOT_DISTURB)
    elif len(shares) > 0:
        last_expire = max(shares.values())
        if you in shares.keys():
            others = list(shares.keys())
            others.remove(you)
            printers.show_granted(
                "Shared", last_expire, highlighted_user=you + " (YOU)", others=others
            )
            printers.show_expire(shares[you], "Your")
        else:
            printers.show_granted("Shared", last_expire, others=shares.keys())
            printers.slock_guide()
    else:
        printers.show_no_lock()

    printers.show_sep_line()


def revoke(who, conn: sqlite3.Connection):
    shares, exclusive = granted(conn)

    cur = conn.cursor()
    if exclusive is not None and who == exclusive[0]:
        cur.execute(defs.SQL.RELEASE, {"who": who})
        assert cur.rowcount == 1
        printers.show_revoke_ok("exclusive", who)
    elif who in shares.keys():
        cur.execute(defs.SQL.RELEASE, {"who": who})
        assert cur.rowcount == 1
        printers.show_revoke_ok("shared", who)
    else:
        printers.warning(defs.Message.NOTHING_REVOKED)
    cur.close()
    conn.commit()


# cannot grant non-current-login users, because the file created would be owned
# by the current login USER
def grant(who: str, want_shared: bool, duration: str, conn: sqlite3.Connection):
    shares, exclusive = granted(conn)
    attempted_expire = datetime.now() + timer.parse_delta(duration)

    already_shared = who in shares
    already_exclusive = exclusive is not None and who == exclusive[0]

    # if already locked, try (upgrade and) prolong
    if already_shared or already_exclusive:
        # won't down grade
        if already_exclusive and want_shared:
            printers.warning(defs.Message.ATTEMP_SLOCK_WITH_XLOCK)
            want_shared = False

        # try upgrade
        if already_shared and not want_shared:
            if len(shares) > 1:
                raise errors.RuntimeErrorWithMessageAndCode(
                    defs.Message.UPGRADE_FAILURE_MSG,
                    defs.Message.UPGRADE_FAILURE_CODE,
                )

            cur = conn.cursor()
            cur.execute(defs.SQL.UPGRADE, {"who": who})
            assert cur.rowcount == 1
            cur.close()
            printers.ok(defs.Message.UPGRADE_OK)

        # try prolong
        old_expire = exclusive[1] if already_exclusive else shares[who]
        if old_expire > attempted_expire:
            printers.warning(defs.Message.ATTEMP_SHORTER_DURATION_THAN_ALREADY_GRANTED)
            printers.show_expire(old_expire, "Your")
        else:
            write_expire(who, want_shared, attempted_expire, conn)
            printers.ok(defs.Message.PROLONG_OK)
            printers.show_expire(attempted_expire, "Your")

    # if neither s- nor x-locked, try lock
    else:
        # cannot want shared when an exclusive is granted
        # cannot want exclusive when some shared or an exclusive is granted
        if (want_shared and exclusive is not None) or (
            not want_shared and (len(shares) > 0 or exclusive is not None)
        ):
            raise errors.RuntimeErrorWithMessageAndCode(
                defs.Message.GRANT_FAILURE_MSG,
                defs.Message.GRANT_FAILURE_CODE,
            )

        write_expire(who, want_shared, attempted_expire, conn)
        printers.show_grant_ok("shared" if want_shared else "exclusive", who)
        printers.show_expire(attempted_expire, "Your")

    conn.commit()
