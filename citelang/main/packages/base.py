__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Custom package managers not in libraries IO

import sys


class PackageManager:
    """
    A package manager is a custom class (not supported by libraries io)
    """

    def __init__(self, *args, **kwargs):
        for attr in ["name", "project_count", "homepage", "color", "default_language"]:
            if not hasattr(self, attr):
                sys.exit(
                    "Misconfigured package manager %s missing %s attribute"
                    % (self.name, attr)
                )

    # If needed, make sure endpoint data is sorted
    def info(self):
        return {
            "name": self.name,
            "project_count": self.project_count,
            "homepage": self.homepage,
            "color": self.color,
            "default_language": self.default_language,
        }

    def package(self, name, **kwargs):
        raise NotImplementedError
