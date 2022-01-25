import imp
import defs


class RuntimeErrorWithMessageAndCode(RuntimeError):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code


def revoke_failure_msg(mode, who):
    return f"Failed to revoke {who}'s {mode} permission."


#########################
# Message printing utils
#########################


def show_sep_line():
    print(f"{defs.FormatCode.HEADER}{'#' * 80}{defs.FormatCode.ENDC}")


def slock_guide():
    print("You can obtain shared access with")
    print(f"\t{defs.Message.SLOCK_CMD}")


def xlock_guide():
    print("You can obtain exclusive access with")
    print(f"\t{defs.Message.XLOCK_CMD}")


def show_no_lock():
    print(f"Neither exclusive nor shared access is not granted yet.")
    slock_guide()
    xlock_guide()


def show_expire(expire):
    print(f"Permission expires at {expire}.")


def show_granted(mode, expire, highlighted_user=None, others=None):
    print(f"{mode} access is granted to")
    if highlighted_user is None:
        who = ", ".join(others)
    else:
        who = f"{defs.FormatCode.BOLD}{highlighted_user}{defs.FormatCode.ENDC}"
        if others is not None:
            who += ", "
            who += ", ".join(others)
    print(f"\t{who},")
    print(
        "(the last of) which expires at "
        f"{defs.FormatCode.BOLD}{expire}{defs.FormatCode.ENDC}."
    )


def show_grant_ok(mode, who):
    ok(f"{who}'s {mode} permission is successfully granted.")


def show_revoke_ok(mode, who):
    ok(f"{who}'s {mode} permission is successfully revoked.")


def ok(msg):
    print(f"{defs.FormatCode.OKGREEN}{msg}{defs.FormatCode.ENDC}")


def warning(msg):
    print(f"{defs.FormatCode.WARNING}{msg}{defs.FormatCode.ENDC}")


# When some op fails within expectation
def failure(msg):
    print(f"{defs.FormatCode.FAIL}{msg}{defs.FormatCode.ENDC}")


# Unexpected errors
def error(msg):
    print(f"{defs.FormatCode.FAIL}{msg}{defs.FormatCode.ENDC}")
