from os.path import join
import re


PROG = "grantme"

SLOCK_CMD = f"{BOLD}{PROG} --mode shared --duration ?d?h?m?s{ENDC}"
XLOCK_CMD = f"{BOLD}{PROG} --mode exclusive --duration ?d?h?m?s{ENDC}"

PROG_DESC = (
    'This is a utility for "granting" exclusive/shared access to '
    "machines. It is purely advisory in the sense that neither permissions "
    "is necessarily required to access the host. Its purpose is to make you "
    "aware of the presence of other active users so that you don't disrupt "
    "their work.\n\n"
    f"Use `{PROG} --mode {{exclusive,shared}} --duration 2h30m to obtain/prolong"
    "permission for 2 hours and 30 minutes.\n"
    f"Use `{PROG} --revoke` to invalidate your granted permission.\n"
    f"Use `{PROG} --revoke --user USER` to invalidate other users' granted"
    "permission.\n"
    f"Use `{PROG} --status` to view permissions of yours and other users'."
)
DURATION_DESC = (
    'Expected aceess duration, formated as "?w?d?h?m?s".'
    f'Default to "30m". You can rerun {PROG} to prolong permission.'
)
USER_DESC = (
    "The user whose permissions should be revoked. Defaults to the current login user."
)
CRY = f"An error occurred, please contact the {PROG} maintainer."


LATCH_FILE = "/run/lock/grant.lock"
DATA_DIR = "/var/lib/grant"
SDIR = join(DATA_DIR, "shared")
XDIR = join(DATA_DIR, "exclusive")

# Formatting codes
# copied from https://stackoverflow.com/a/287944
HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKCYAN = "\033[96m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
ENDC = "\033[0m"

HEADER_LINE = f"{HEADER}{'#' * 80}{ENDC}"


EXPIRE_FORMAT = "%Y-%m-%d %H:%M:%S"
DELTA_REGEX = re.compile(
    r"^((?P<weeks>[\.\d]+?)w)? *"
    r"^((?P<days>[\.\d]+?)d)? *"
    r"((?P<hours>[\.\d]+?)h)? *"
    r"((?P<minutes>[\.\d]+?)m)? *"
    r"((?P<seconds>[\.\d]+?)s?)?$"
)

# a global error flag
ERR = 255
