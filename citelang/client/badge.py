__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.main.client as client
from citelang.logger import logger
import tempfile
import os


def main(args, parser, extra, subparser):
    if os.path.isfile(args.package[1]):
        cli = client.get_parser(filename=args.package[1], quiet=args.quiet)
        result = cli.badge(
            name=args.package[0],
            use_cache=not args.no_cache,
            max_depth=args.max_depth,
            max_deps=args.max_depth,
            min_credit=args.min_credit,
            credit_split=args.credit_split,
            template=args.template,
        )

    # Case 2: named package and manager
    else:
        cli = client.Client(quiet=args.quiet)
        result = cli.badge(
            name=args.package[1],
            manager=args.package[0],
            use_cache=not args.no_cache,
            max_depth=args.max_depth,
            max_deps=args.max_depth,
            min_credit=args.min_credit,
            credit_split=args.credit_split,
            template=args.template,
        )

    if not args.outfile and args.template == "static":
        args.outfile = os.path.join(
            "%s-%s.png" % (args.package[0], args.package[1])
        ).replace(os.sep, "-")

    elif not args.outfile:
        args.outfile = os.path.join(tempfile.mkdtemp(), "index.html")

    if os.path.exists(args.outfile) and not args.force:
        logger.exit(f"{args.outfile} exists, add --force to overwrite.")
    result.save(args.outfile)
