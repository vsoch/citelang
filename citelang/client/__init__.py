#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang
from citelang.logger import setup_logger
import citelang.main.endpoints as endpoints
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(
        description="CiteLang",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global Variables
    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--no-cache",
        dest="no_cache",
        help="disable using the cache for any particular command.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--settings-file",
        dest="settings_file",
        help="custom path to settings file.",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="show software version.",
        default=False,
        action="store_true",
    )

    description = "actions"
    subparsers = parser.add_subparsers(
        help="actions",
        title="actions",
        description=description,
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", description="show software version")

    # List package managers available
    ls = subparsers.add_parser(
        "list", description="list package managers available to derive citations from."
    )
    ls.add_argument("--json", help="output json", default=False, action="store_true")
    ls.add_argument("--all", help="output json", default=False, action="store_true")
    ls.add_argument("--outfile", "-o", help="write content to output file")

    # Get a package
    pkg = subparsers.add_parser(
        "package",
        description="list package managers available to derive citations from.",
    )
    pkg.add_argument("package", help="package manager and name to parse", nargs=2)
    pkg.add_argument(
        "--json",
        dest="json",
        help="print output to json.",
        default=False,
        action="store_true",
    )
    pkg.add_argument("--outfile", "-o", help="Save to an output json file.")

    # Local shell with client loaded
    shell = subparsers.add_parser(
        "shell",
        description="shell into a Python session with a client.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    shell.add_argument(
        "--interpreter",
        "-i",
        dest="interpreter",
        help="python interpreter",
        choices=["ipython", "python", "bpython"],
        default="ipython",
    )

    # Custom config
    config = subparsers.add_parser(
        "config",
        description="update configuration settings. Use set or get to see or set information.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    config.add_argument(
        "--central",
        dest="central",
        help="make edits to the central config file.",
        default=False,
        action="store_true",
    )

    config.add_argument(
        "params",
        nargs="*",
        help="""Set or get a config value, edit the config, add or remove a list variable, or create a user-specific config.
citelang config set key:value
citelang config get key
citelang edit
citelang config inituser""",
        type=str,
    )
    return parser


def run():

    parser = get_parser()

    def help(return_code=0):
        version = citelang.__version__

        print("\nCiteLang Client v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(citelang.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # retrieve subparser (with help) from parser
    helper = None
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                helper = subparser
                break

    if args.command == "config":
        from .config import main
    elif args.command == "shell":
        from .shell import main
    elif args.command == "list":
        from .listing import main
    elif args.command == "package":
        from .package import main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args=args, parser=parser, extra=extra, subparser=helper)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1

    help(return_code)


if __name__ == "__main__":
    run()
