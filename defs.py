from os.path import join
import re


PROG = "grantme"

LATCH_FILE = "/run/lock/grant.lock"
DATA_DIR = "/var/lib/grant"
SDIR = join(DATA_DIR, "shared")
XDIR = join(DATA_DIR, "exclusive")

EXPIRE_FORMAT = "%Y-%m-%d %H:%M:%S"
DELTA_REGEX = re.compile(
    r"^((?P<weeks>[\.\d]+?)w)? *"
    r"^((?P<days>[\.\d]+?)d)? *"
    r"((?P<hours>[\.\d]+?)h)? *"
    r"((?P<minutes>[\.\d]+?)m)? *"
    r"((?P<seconds>[\.\d]+?)s?)?$"
)


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
        'Expected aceess duration, formated as "?w?d?h?m?s".'
        f'Default to "30m". You can rerun {PROG} to prolong permission.'
    )
    USER_HELP = (
        "The user whose permissions should be revoked."
        "Defaults to the current login user."
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


# Formatting codes
# copied from https://stackoverflow.com/a/287944
class FormatCode:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ENDC = "\033[0m"
