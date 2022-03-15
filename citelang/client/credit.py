__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.main import Client


def main(args, parser, extra, subparser):

    cli = Client(quiet=args.quiet, settings_file=args.settings_file)
    result = cli.credit(
        name=args.package[1],
        manager=args.package[0],
        use_cache=not args.no_cache,
        max_depth=args.max_depth,
        max_deps=args.max_depth,
        min_credit=args.min_credit,
        credit_split=args.credit_split,
    )

    if args.json and not args.outfile:
        result.print_json()

    elif args.outfile:
        result.save(args.outfile)

    else:
        result.print_result()
