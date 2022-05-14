#!/usr/bin/env python3

import argparse
import sqlite3
import sys
from getpass import getuser
from traceback import print_tb

import defs
import procedures
from utils import errors, printers


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
    args = parser.parse_args()

    try:
        conn = sqlite3.connect(defs.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row

        if args.status:
            procedures.print_status(conn)
        elif args.revoke:
            procedures.revoke(args.user, conn)
        elif args.mode is not None:
            assert args.mode == "shared" or args.mode == "exclusive"
            procedures.grant(args.mode == "shared", args.duration, conn)
        else:
            parser.print_help()
    except errors.RuntimeErrorWithMessageAndCode as err:
        printers.error(err.msg)
        conn.close()
        sys.exit(err.code)
    except Exception as err:
        printers.error("Unexpected error: {err}".format(err=err))
        print_tb(err.__traceback__)
        conn.close()
        sys.exit(defs.Message.UNEXPECTED_ERROR_CODE)


if __name__ == "__main__":
    main()
