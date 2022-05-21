#!/usr/bin/env python3

import argparse
import sqlite3
import sys
from getpass import getuser
from traceback import print_tb

from . import defs
from . import procedures
from .utils import errors, printers


def main():
    current_user = getuser()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(defs.Message.PROG_HELP),
    )
    parser.add_argument("-s", "--status", action="store_true")
    parser.add_argument("-m", "--mode", choices=["exclusive", "shared"])
    parser.add_argument(
        "-d", "--duration", default="30m", help=defs.Message.DURATION_HELP
    )
    parser.add_argument("-r", "--revoke", action="store_true")
    parser.add_argument(
        "-u", "--user", default=current_user, help=defs.Message.USER_HELP
    )
    parser.add_argument(
        "-i", "--init", action="store_true", help=defs.Message.INIT_HELP
    )

    args = parser.parse_args()

    try:
        if args.init:
            defs.DATA_DIR.mkdir(parents=True, exist_ok=True)
            defs.DATA_DIR.chmod(defs.DATA_DIR.stat().st_mode | 0o666)

        conn = sqlite3.connect(
            str(defs.DB_FILE), uri=True, detect_types=sqlite3.PARSE_DECLTYPES
        )
        conn.row_factory = sqlite3.Row

        if args.init:
            defs.DB_FILE.chmod(defs.DB_FILE.stat().st_mode | 0o666)
    except Exception as err:
        printers.error(
            "Failed to connect the database. "
            f"Please ensure that {defs.DB_FILE} exists or "
            "you have root privilege when creating one. "
            f"To resolve corrupted database files, you may remove {defs.DB_FILE} "
            f"and then run `{defs.PROG} --init` to create a new one."
        )
        printers.error(f"Original exception message: {err}")
        sys.exit(defs.Message.UNEXPECTED_ERROR_CODE)

    try:
        exit_code = 0

        if args.init:
            procedures.setup_db(conn)
        elif args.status:
            procedures.print_status(current_user, conn)
        elif args.revoke:
            procedures.revoke_and_print_result(args.user, conn)
        elif args.mode is not None:
            assert args.mode == "shared" or args.mode == "exclusive"
            procedures.grant_and_print_result(
                current_user, args.mode == "shared", args.duration, conn
            )
        else:
            parser.print_help()
    except errors.RuntimeErrorWithMessageAndCode as err:
        printers.error(err.msg)
        exit_code = err.code
    except Exception as err:
        printers.error("Unexpected error: {err}".format(err=err))
        print_tb(err.__traceback__)
        exit_code = defs.Message.UNEXPECTED_ERROR_CODE
    finally:
        conn.close()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
