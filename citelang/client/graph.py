__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.main import Client


def main(args, parser, extra, subparser):

    cli = Client(quiet=args.quiet, settings_file=args.settings_file)
    cli.graph(
        name=args.package[1],
        manager=args.package[0],
        use_cache=not args.no_cache,
        min_credit=args.min_credit,
        max_depth=args.max_depth,
        max_deps=args.max_deps,
        credit_split=args.credit_split,
        fmt=args.fmt,
    )
