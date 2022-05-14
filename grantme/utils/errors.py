class RuntimeErrorWithMessageAndCode(RuntimeError):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code


def revoke_failure_msg(mode, who):
    return "Failed to revoke {who}'s {mode} permission.".format(who=who, mode=mode)
