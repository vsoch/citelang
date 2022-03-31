__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.main.settings as settings
import citelang.defaults as defaults
from citelang.logger import logger
import sys


def main(args, parser, extra, subparser):

    # If nothing provided, show help
    if not args.params:
        print(subparser.format_help())
        sys.exit(0)

    # The first "param" is either set of get
    command = args.params.pop(0)

    # init global settings
    validate = True if not command == "edit" else False

    # If the user wants the central config file
    if args.central:
        cfg = settings.SettingsBase(
            settings_file=defaults.default_settings_file, validate=validate
        )
    else:
        cfg = settings.SettingsBase(validate=validate)

    # For each new setting, update and save!
    if command == "inituser":
        return cfg.inituser()
    if command == "edit":
        return cfg.edit()

    if command in ["set", "add", "remove"]:

        # Update each param
        for param in args.params:
            cfg.update_param(command, param)

        # Save settings
        cfg.save()

    # For each get request, print the param pair
    elif command == "get":
        for key in args.params:
            value = cfg.get(key)
            value = value or "is unset"
            logger.info("%s %s" % (key.ljust(30), value))

    else:
        logger.error("%s is not a recognized command." % command)
