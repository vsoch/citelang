__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.main.base as base
import citelang.main.parser as parser

Client = base.BaseClient


def get_parser(filename=None, *args, **kwargs):
    """
    Get a parser based on a filename. A GraphClient is required.
    """
    if not filename:
        return parser.FileNameParser(*args, **kwargs)
    if filename.endswith(".md"):
        return parser.FileNameParser(filename=filename, *args, **kwargs)
    return parser.RequirementsParser(filename=filename, *args, **kwargs)
