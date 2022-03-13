__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.main import Client
import citelang.utils as utils


def main(args, parser, extra, subparser):

    cli = Client(quiet=args.quiet, settings_file=args.settings_file)
    result = cli.package_managers(use_cache=not args.no_cache)

    # Default limit is 25, unless --all provided
    if args.json and not args.outfile:
        result.print_json()

    elif args.outfile:
        result.save(args.outfile)

    else:
        result.table()
