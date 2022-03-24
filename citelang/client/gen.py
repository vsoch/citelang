__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.main import Client
import citelang.utils as utils


def main(args, parser, extra, subparser):

    cli = Client(quiet=args.quiet, settings_file=args.settings_file)
    result = cli.gen(
        name=args.package[1],
        manager=args.package[0],
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
