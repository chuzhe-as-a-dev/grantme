#!/usr/bin/env python3

import argparse
import atexit
import os
import shutil
import socket
import sqlite3
import sys
from getpass import getuser
from pathlib import Path
from traceback import print_tb

from grantme.constants.misc import PROG
from grantme.constants.msgs import DURATION_HELP, INIT_HELP, PROG_HELP, USER_HELP
from grantme.procedures import (
    grant_and_print_result,
    list_users,
    print_status,
    revoke_and_print_result,
)
from grantme.utils.config import read_data_dir
from grantme.utils.errors import UNEXPECTED_ERROR_CODE, GrantmeError
from grantme.utils.printers import error, ok, show_path_hint
from grantme.utils.setup import create_db


DB_FILENAME = "db.sqlite3"
# looked up next to the launcher script, i.e., bin/grantme.conf
CONF_FILENAME = "grantme.conf"
# default data directory, relative to the repository root; its content is
# untracked by git
STATE_DIRNAME = "state"


def main():
    current_user = getuser()
    bin_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    # not installed globally, so remind users who call it by its full path; shown
    # at exit so that it follows the actual output
    if shutil.which(PROG) is None:
        atexit.register(show_path_hint, bin_dir)

    # GRANTME_DIR overrides the config file (used by tests)
    if "GRANTME_DIR" in os.environ:
        data_dir = Path(os.environ["GRANTME_DIR"])
    else:
        conf_file = Path(bin_dir) / CONF_FILENAME
        data_dir = read_data_dir(
            conf_file,
            socket.gethostname().split(".")[0],
            Path(bin_dir).parent / STATE_DIRNAME,
        )
    db_file = data_dir / DB_FILENAME

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(PROG_HELP),
    )
    parser.add_argument("-s", "--status", action="store_true")
    parser.add_argument("-m", "--mode", choices=["exclusive", "shared"])
    parser.add_argument("-d", "--duration", default="30m", help=DURATION_HELP)
    parser.add_argument("-r", "--revoke", action="store_true")
    parser.add_argument("-u", "--user", default=current_user, help=USER_HELP)
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-i", "--init", action="store_true", help=INIT_HELP)

    args = parser.parse_args()

    if args.init:
        try:
            create_db(data_dir, db_file)
        except Exception as err:
            error(
                "Failed to initiate the database. Please ensure that you have write"
                " permission for creating {db} file. To resolve corrupted"
                " database files, you may remove {db} and then run"
                " `{prog} --init` to create a new one.".format(db=db_file, prog=PROG)
            )
            error("Original exception: {}".format(err))
            sys.exit(UNEXPECTED_ERROR_CODE)
        ok("Database initiated at {}.".format(db_file))
        sys.exit(0)

    if not db_file.exists():
        error(
            "Database {} does not exist. Please ask the maintainer to run"
            " `{} --init`.".format(db_file, PROG)
        )
        sys.exit(UNEXPECTED_ERROR_CODE)

    conn = None
    try:
        exit_code = 0

        conn = sqlite3.connect(str(db_file), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        # hold the write lock from reading status to writing leases, so that
        # concurrent invocations cannot both pass the checks
        conn.execute("begin immediate")

        if args.status:
            print_status(current_user, conn)
        elif args.list:
            list_users(conn)
        elif args.revoke:
            revoke_and_print_result(args.user, conn)
        elif args.mode is not None:
            assert args.mode in ("shared", "exclusive")
            grant_and_print_result(
                current_user, args.mode == "shared", args.duration, conn
            )
        else:
            print_status(current_user, conn)
    except GrantmeError as err:
        error(err.msg)
        exit_code = err.code
    except Exception as err:
        error("Unexpected exception: {}".format(err))
        print_tb(err.__traceback__)
        exit_code = UNEXPECTED_ERROR_CODE
    finally:
        if conn is not None:
            conn.close()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
