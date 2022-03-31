__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.main.client import get_parser
import citelang.utils as utils


def main(args, parser, extra, subparser):

    cli = get_parser(
        filename=args.filename, quiet=args.quiet, settings_file=args.settings_file
    )
    result = cli.parse(
        use_cache=not args.no_cache,
        max_depth=args.max_depth,
        max_deps=args.max_depth,
        min_credit=args.min_credit,
        credit_split=args.credit_split,
    )

    if args.outfile:
        utils.write_file(result.render(), args.outfile)
        print("Saved to %s" % args.outfile)
    else:
        print(result.render())
