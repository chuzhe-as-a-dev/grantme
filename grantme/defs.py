from os.path import join
from pathlib import Path

PROG = "grantme"

DATA_DIR = Path("/var/lib/grantme")
DB_FILENAME = "db.sqlite3"
DB_FILE = DATA_DIR / DB_FILENAME


class SQL:
    CREATE_DB = (
        "create table if not exists leases ("
        "  user      TEXT constraint leases_pk primary key,"
        "  shared    INTEGER not null,"
        "  expire_at timestamp not null"
        ");"
    )
    CREATE_INDEX = (
        "create index if not exists leases_expire_at_index on leases (expire_at);"
    )
    QUERY_SHARED = (
        "select user, expire_at from leases where shared = true and expire_at > :now;"
    )
    QUERY_EXCLUSIVE = (
        "select user, expire_at from leases where shared = false and expire_at > :now;"
    )
    UPSERT = (
        "insert into leases values (:who, :shared, :expire_at)"
        "  on conflict do update set shared=:shared, expire_at=:expire_at;"
    )
    UPGRADE = "update leases set shared = false where user = :who and shared = true;"
    RELEASE = "delete from leases where user = :who;"


class Message:
    # Help messages
    PROG_HELP = (
        'This is a utility for "granting" exclusive/shared access to '
        "machines. It is purely advisory in the sense that neither permissions "
        "is necessarily required to access the host. Its purpose is to make you "
        "aware of the presence of other active users so that you don't disrupt "
        "their work.\n\n"
        "Use `{prog} --mode {{exclusive,shared}} --duration 2h30m to obtain/prolong"
        "permission for 2 hours and 30 minutes.\n"
        "Use `{prog} --revoke` to invalidate your granted permission.\n"
        "Use `{prog} --revoke --user USER` to invalidate other users' granted"
        "permission.\n"
        "Use `{prog} --status` to view permissions of yours and other users'.".format(
            prog=PROG
        )
    )
    DURATION_HELP = (
        'Expected aceess duration, formated as "?w?d?h?m?s". '
        'Default to "30m". You can rerun {prog} to prolong permission.'.format(
            prog=PROG
        )
    )
    USER_HELP = (
        "The user whose permissions should be revoked. "
        "Defaults to the current login user."
    )
    INIT_HELP = (
        "Initialize the backend database. "
        "Root privilege might be needed (i.e., `sudo`)."
    )

    # Info
    SLOCK_CMD = "{prog} --mode shared --duration ?d?h?m?s".format(prog=PROG)
    XLOCK_CMD = "{prog} --mode exclusive --duration ?d?h?m?s".format(prog=PROG)
    PROLONG_OK = "Permission is successfully prolonged."
    UPGRADE_OK = "Shared permission upgraded to an exclusive permission."

    # Warnings
    DO_NOT_DISTURB = "Please **AVOID DEMANDING TASKS**, so as to not disrupt others."
    NOTHING_REVOKED = "No permission is currently granted; nothing is revoked."
    ATTEMP_SLOCK_WITH_XLOCK = (
        "An exclusive permission already exists. Ignoring `--mode shared`."
    )
    ATTEMP_SHORTER_DURATION_THAN_ALREADY_GRANTED = (
        "A permission that expires later than the given duration already exists."
        "No change is made."
    )

    # Failure messages
    LATCH_FAILURE_MSG = (
        "Another user is attempting to change permissions. Please retry again."
    )
    LATCH_FAILURE_CODE = 4
    PROLONG_FAILURE_MSG = "Failed to prolong permission."
    PROLONG_FAILURE_CODE = 5
    UPGRADE_FAILURE_MSG = "Failed to upgrade shared permission to exclusive permission."
    UPGRADE_FAILURE_CODE = 6
    GRANT_FAILURE_MSG = "Failed to grant permission."
    GRANT_FAILURE_CODE = 7

    # Error messages and codes
    DIR_ERROR_MSG = "Data directory does not exist or is not complete."
    DIR_ERROR_CODE = 1
    EXCLUSION_ERROR_MSG = "More than one users are granted exclusive access."
    EXCLUSION_ERROR_CODE = 2
    REVOKE_ERROR_CODE = 3
    UNEXPECTED_ERROR_CODE = 255
