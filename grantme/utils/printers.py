import sys
from datetime import datetime
from typing import Mapping, Optional

from grantme.constants.msgs import GRANT_CMD, SLOCK_CMD


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


INDENT = "  "


def bold(text: str) -> str:
    return FormatCode.BOLD + text + FormatCode.ENDC


def format_time(t: datetime) -> str:
    return t.strftime("%Y-%m-%d %H:%M")


def format_left(t: datetime) -> str:
    # round to minutes, so that a fresh 2h grant shows "2h" rather than "1h 59m"
    mins = int(round((t - datetime.now()).total_seconds() / 60))
    if mins < 1:
        return "<1m"
    days, mins = divmod(mins, 1440)
    hours, mins = divmod(mins, 60)
    parts = []
    if days:
        parts.append("{}d".format(days))
    if hours:
        parts.append("{}h".format(hours))
    if mins and not days:
        parts.append("{}m".format(mins))
    return " ".join(parts)


def format_until(t: datetime, highlight: bool = True) -> str:
    time = format_time(t)
    return "until {} ({} left)".format(bold(time) if highlight else time, format_left(t))


def format_holders(user_expires: Mapping[str, datetime]) -> str:
    """Plain one-line summary of holders, for error messages."""
    return "{} {}".format(
        ", ".join(user_expires.keys()),
        format_until(max(user_expires.values()), highlight=False),
    )


def show_sep_line():
    print(FormatCode.HEADER, "#" * 80, FormatCode.ENDC, sep="")


def show_free():
    print(FormatCode.OKGREEN + bold("The machine is free.") + FormatCode.ENDC)
    print("Get access with `{}`.".format(GRANT_CMD))


def show_holders(exclusive: bool, user_expires: Mapping[str, datetime], you: str):
    if you in user_expires:
        color = FormatCode.OKGREEN
    elif exclusive:
        color = FormatCode.FAIL
    else:
        color = FormatCode.WARNING
    mode = "EXCLUSIVE" if exclusive else "SHARED"
    print(color + bold(mode) + color + " access is held by:" + FormatCode.ENDC)

    names = {user: user + " (you)" if user == you else user for user in user_expires}
    width = max(len(name) for name in names.values())
    for user, expire_at in sorted(user_expires.items(), key=lambda item: item[1]):
        print(INDENT + names[user].ljust(width) + "  " + format_until(expire_at))


def slock_guide():
    print("You can also get shared access with `{}`.".format(SLOCK_CMD))


def show_path_hint(bin_dir: str):
    print(
        FormatCode.WARNING
        + "Hint: `grantme` is not in your PATH. Add it with:\n"
        + INDENT
        + "echo 'export PATH=\"{}:$PATH\"' >> ~/.bashrc".format(bin_dir)
        + FormatCode.ENDC,
        file=sys.stderr,
    )


def ok(msg):
    print(FormatCode.OKGREEN + msg + FormatCode.ENDC)


def info(msg):
    print(FormatCode.OKBLUE + msg + FormatCode.ENDC)


def warning(msg):
    print(FormatCode.WARNING + msg + FormatCode.ENDC)


# When some op fails within expectation
def failure(msg):
    print(FormatCode.FAIL + msg + FormatCode.ENDC)


# Unexpected errors
def error(msg):
    print(FormatCode.FAIL + msg + FormatCode.ENDC)
