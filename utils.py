import imp
import defs


class RuntimeErrorWithMessageAndCode(RuntimeError):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code


def revoke_failure_msg(mode, who):
    return "Failed to revoke {who}'s {mode} permission.".format(who=who, mode=mode)


#########################
# Message printing utils
#########################


def show_sep_line():
    print(defs.FormatCode.HEADER, "#" * 80, defs.FormatCode.ENDC, sep="")


def slock_guide():
    print("You can obtain shared access with")
    print("\t" + defs.Message.SLOCK_CMD)


def xlock_guide():
    print("You can obtain exclusive access with")
    print("\t" + defs.Message.XLOCK_CMD)


def show_no_lock():
    print("Neither exclusive nor shared access is not granted yet.")
    slock_guide()
    xlock_guide()


def show_expire(expire, whose=None):
    if whose is None:
        subject = "The permission"
    else:
        subject = "{whose} permission".format(whose=whose)
    print("{subject} expires at {expire}.".format(subject=subject, expire=expire))


def show_granted(mode, expire, highlighted_user=None, others=[]):
    print(mode, "access is granted to")
    if highlighted_user is None:
        who = ", ".join(others)
    else:
        who = defs.FormatCode.BOLD + highlighted_user + defs.FormatCode.ENDC
        if len(others) > 0:
            who += ", "
            who += ", ".join(others)
    print("\t" + who)
    print(
        "(the last of) which expires at "
        + defs.FormatCode.BOLD
        + str(expire)
        + defs.FormatCode.ENDC
        + "."
    )


def show_grant_ok(mode, who):
    ok("{who}'s {mode} permission is successfully granted.".format(who=who, mode=mode))


def show_revoke_ok(mode, who):
    ok("{who}'s {mode} permission is successfully revoked.".format(who=who, mode=mode))


def ok(msg):
    print(defs.FormatCode.OKGREEN + msg + defs.FormatCode.ENDC)


def warning(msg):
    print(defs.FormatCode.WARNING + msg + defs.FormatCode.ENDC)


# When some op fails within expectation
def failure(msg):
    print(defs.FormatCode.FAIL + msg + defs.FormatCode.ENDC)


# Unexpected errors
def error(msg):
    print(defs.FormatCode.FAIL + msg + defs.FormatCode.ENDC)
