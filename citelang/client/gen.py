__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.main.client as client
import citelang.utils as utils
import os


def main(args, parser, extra, subparser):

    # Case 1: only one thing provided to package, and exists as a file
    if os.path.isfile(args.package[1]):
        cli = client.get_parser(filename=args.package[1], quiet=args.quiet)
        result = cli.gen(
            name=args.package[0],
            use_cache=not args.no_cache,
            max_depth=args.max_depth,
            max_deps=args.max_depth,
            min_credit=args.min_credit,
            credit_split=args.credit_split,
        )

    # Case 2: named package and manager
    else:
        cli = client.get_parser()
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
