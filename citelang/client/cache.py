__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.main.cache as cache
import citelang.main.settings as settings


def main(args, parser, extra, subparser):

    # init global settings
    cli = cache.cache

    if args.clear:
        cli.clear(force=args.force)
    else:
        print(settings.cfg.cache_dir)
