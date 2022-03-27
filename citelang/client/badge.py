__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.main import Client
from citelang.logger import logger
import tempfile
import os


def main(args, parser, extra, subparser):

    cli = Client(quiet=args.quiet, settings_file=args.settings_file)
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
        args.outfile = os.path.join("%s-%s.png" % (args.package[0], args.package[1]))

    elif not args.outfile:
        args.outfile = os.path.join(tempfile.mkdtemp(), "index.html")

    if os.path.exists(args.outfile) and not args.force:
        logger.exit(f"{args.outfile} exists, add --force to overwrite.")
    result.save(args.outfile)
