__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Custom package managers not in libraries IO

import os
import sys

import requests

import citelang.main.cache as cache
import citelang.main.endpoints as endpoints
import citelang.utils as utils
from citelang.logger import logger


class PackageManager:
    """
    A package manager is a custom class (not supported by libraries io)
    """

    underlying_manager = None
    filesystem_manager = False

    def __init__(self, *args, **kwargs):
        self.cache = cache.cache
        self.data = {}
        for attr in [
            "name",
            "project_count",
            "homepage",
            "color",
            "default_language",
            "default_versions",
        ]:
            if not hasattr(self, attr):
                sys.exit(
                    "Misconfigured package manager %s missing %s attribute"
                    % (self.name, attr)
                )

    # If needed, make sure endpoint data is sorted
    def info(self):
        return {
            "name": self.underlying_manager or self.name,
            "project_count": self.project_count,
            "homepage": self.homepage,
            "color": self.color,
            "default_language": self.default_language,
        }

    def get_or_fail(self, url, headers=None, return_text=False):
        """
        Shared endpoint to get a url or fail.
        """
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.exit("Cannot retrieve %s: %s" % (url, response.json()))
        if return_text:
            return response.text
        return response.json()

    def package(self, name, **kwargs):
        raise NotImplementedError


class PackagesFromFile(PackageManager):
    """
    Load packages from file. The class requires a parse function to parse
    the content provided.
    """

    filesystem_manager = True

    def __init__(self, package_name=None, content=None, filename=None):
        """
        An base filesystem package manager parses packages from a file
        """
        self.version = None
        self.package_name = package_name
        super().__init__()
        if package_name:
            self.set_name(package_name)
        self.data = {}
        self.filename = filename
        if content:
            self.parse(content)

    def set_name(self, name):
        if "@" in name:
            name, version = name.split("@", 1)
            self.version = version
        if "[" in name and "]" in name:
            name = name.split("[", 1)[0]

        # invalid characters found!
        name = name.replace(";", "")
        self.package_name = name

    def get_package(self, package_name, version=None):
        """
        Shared function to get a package based on name, version
        """
        # Try to get from cache - either versioned or not
        pkg = None
        if package_name and version:
            cache_name = f"package/{self.underlying_manager}/{package_name}/{version}"
            result = self.cache.get(cache_name)
            if result:
                pkg = endpoints.get_endpoint("package", data=result)

        elif package_name and not version:
            cache_name = f"package/{self.underlying_manager}/{package_name}"
            result = self.cache.get(cache_name)
            if result:
                pkg = endpoints.get_endpoint("package", data=result)

        if pkg is None:

            # Don't try again if this package is flagged as empty (not existing)
            if self.cache.is_empty(f"package/{self.underlying_manager}/{package_name}"):
                return pkg
            try:
                pkg = endpoints.get_endpoint(
                    "package",
                    package_name=package_name,
                    manager=self.underlying_manager,
                )
            except Exception:
                pass

        # If we get down here and no package, mark empty (unless it isn't a package we know)
        if not pkg:
            try:
                self.cache.mark_empty(
                    f"package/{self.underlying_manager}/{package_name}"
                )
            except Exception:
                pass
        return pkg

    def get_repo(self):
        """
        Helper function to return start of repo metadata. Intended to be used
        in the self.parse() function.
        """
        # The "repo" is the package name, we can't be sure about versions
        versions = [
            {
                "published_at": utils.get_time_now(),
                "number": self.version or "latest",
            }
        ]
        repo = {"name": self.package_name, "versions": versions}

        # Try to provide a default version
        repo["default_version"] = self.version or "latest"
        return repo

    def package(self, name, **kwargs):
        """
        The package endpoint ignores the name and just returns parsed data
        """
        return self.data.get("package")

    def from_file(self, filename, **kwargs):
        """
        From file reads in the filename and presents to parse.

        This is a means for a specific package manager to be used directly.
        We trust the user to provide the correct content file to parse.
        """
        self.filename = os.path.abspath(filename)
        content = utils.read_file(filename)
        return self.parse(content, **kwargs)

    def parse(self, content, **kwargs):
        """
        Parse the self.content
        """
        raise NotImplementedError
