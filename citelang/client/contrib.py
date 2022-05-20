__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.main.client as client
import citelang.utils as utils
from citelang.logger import logger
import citelang.main.result as results


def main(args, parser, extra, subparser):
    parser = client.ContributionParser(
        root=args.root, start=args.start, end=args.end, outdir=args.outdir
    )

    # All time true means we include git blames done before the range
    summary = parser.parse(within_range=not args.all_time, shallow=args.shallow)

    if args.by == "author":
        data = summary.by_author(args.detail, filters=args.filters)
    else:
        data = summary.by_file(args.detail, filters=args.filters)

    # Do we want to save data to file?
    if args.outfile:
        logger.info("Saving to %s" % args.outfile)
        utils.write_json(data, args.outfile)
        return

    # Otherwise, parse into table
    if args.detail:

        # Separate paths by newlines
        for item in data:
            item["paths"] = "\n".join(
                ["%s: %s" % (k, v) for k, v in item["paths"].items()]
            )
        table = results.Table(data)
    else:
        table = results.Table(data)
    table.table(limit=None)
