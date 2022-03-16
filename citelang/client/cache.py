__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.main import Client


def main(args, parser, extra, subparser):

    cli = Client(quiet=args.quiet, settings_file=args.settings_file)

    if args.clear:
        cli.clear_cache(force=args.force)
    else:
        print(cli.settings.cache_dir)
