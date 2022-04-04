__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.main import Client


def main(args, parser, extra, subparser):

    cli = Client(quiet=args.quiet)
    result = cli.package_managers(use_cache=not args.no_cache)

    if args.json and not args.outfile:
        result.print_json()

    elif args.outfile:
        result.save(args.outfile)

    else:
        limit = 25
        if args.all:
            limit = None
        result.table(limit=limit)
