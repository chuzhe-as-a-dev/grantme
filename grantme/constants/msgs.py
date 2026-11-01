# Help messages
from grantme.constants.misc import PROG


PROG_HELP = (
    'This is a utility for "granting" exclusive/shared access to '
    "machines. It is purely advisory in the sense that neither permissions "
    "is necessarily required to access the host. Its purpose is to make you "
    "aware of the presence of other active users so that you don't disrupt "
    "their work.\n\n"
    "Use `{prog} --mode {{exclusive,shared}} --duration 2h30m` to obtain/prolong "
    "permission for 2 hours and 30 minutes.\n"
    "Use `{prog} --revoke` to invalidate your granted permission.\n"
    "Use `{prog} --revoke --user USER` to invalidate other users' granted "
    "permission.\n"
    "Use `{prog} --status` to view permissions of yours and other users'.".format(
        prog=PROG
    )
)
INIT_HELP = (
    "Initialize the backend database. Run once by the maintainer when deploying to a"
    " machine."
)
DURATION_HELP = (
    'Expected access duration, formatted as "?w?d?h?m?s". Default to "30m". You can'
    " rerun {prog} to prolong permission.".format(prog=PROG)
)
USER_HELP = (
    "The user whose permissions should be revoked. Defaults to the current login user."
)

# Info
GRANT_CMD = "{prog} --mode {{shared,exclusive}} --duration ?d?h?m?s".format(prog=PROG)
SLOCK_CMD = "{prog} --mode shared --duration ?d?h?m?s".format(prog=PROG)
GRANT_OK = "Granted {mode} access to {who} {until}."
PROLONG_OK = "Prolonged {who}'s {mode} access {until}."
UPGRADE_OK = "Upgraded {who}'s access to exclusive {until}."
REVOKE_OK = "Revoked {who}'s {mode} access."

# Warnings
DO_NOT_DISTURB = "Please AVOID DEMANDING TASKS so as not to disrupt them."
NOTHING_REVOKED = "{who} holds no access; nothing is revoked."
ATTEMPT_SLOCK_WITH_XLOCK = "{who} already holds exclusive access; keeping it exclusive."
ATTEMPT_SHORTER_DURATION_THAN_ALREADY_GRANTED = (
    "{who}'s {mode} access already lasts longer; unchanged {until}."
)
