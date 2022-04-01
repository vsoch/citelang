__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Parse a requirements.txt file to generate a "package"
import citelang.main.endpoints as endpoints
import citelang.utils as utils

import re

from .base import PackageManager


class RequirementsManager(PackageManager):
    """
    Packages from GitHub, either release, or branch.
    """

    name = "requirements.txt"
    underlying_manager = "pypi"
    default_language = None
    project_count = None
    homepage = "pypi.org/"
    color = "#006dad"
    default_language = "Python"
    default_versions = None

    def __init__(self, package_name=None, content=None):
        """
        A requirements manager, unlike other custom packages, does parsing
        of dependencies that are provided in content (a list read from
        requirements.txt) and ignores the name passed to package or dependencies.
        """
        self.version = None
        self.package_name = package_name
        super().__init__()
        if package_name:
            self.set_name(package_name)
        self.data = {}
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

    def parse(self, content):
        """
        Parse the self.content (the requirements.txt file)
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

        # Dependencies we parse as pypi packages
        # This should also update the cache and make it easier to retrieve later
        deps = []
        for line in content.split("\n"):

            # We can't easily add github pypi references
            if not line or "git@" in line:
                continue

            version = None
            package_name = line.strip()
            if re.search("(==|<=|>=)", package_name):
                package_name, _, version = re.split("(==|<=|>=)", package_name)

            # We cannot parse a dep without a name
            if not package_name:
                continue

            # First add requirements (names and pypi manager) to deps

            # Try to get from cache - either versioned or not
            if package_name and version:
                cache_name = f"package/pypi/{package_name}/{version}"
                result = self.cache.get(cache_name)
                if result:
                    pkg = endpoints.get_endpoint("package", data=result)

            elif package_name and not version:
                cache_name = f"package/pypi/{package_name}"
                result = self.cache.get(cache_name)
                if result:
                    pkg = endpoints.get_endpoint("package", data=result)

            else:
                pkg = endpoints.get_endpoint(
                    "package", package_name=package_name, manager="pypi"
                )

            # Ensure we have version, fallback to latest
            if not version:
                version = pkg.data["latest_release_number"]

            # Require saving to cache here - many expensive calls
            cache_name = f"package/pypi/{package_name}/{version}"
            self.cache.set(cache_name, pkg)

            # use latest release version. This will be wrong for an old
            # dependency, but it's not worth it to make a ton of extra API calls
            dep = {
                "name": package_name,
                "project_name": package_name,
                "number": version,
                "published_at": pkg.data["latest_stable_release_published_at"],
                "researched_at": None,
                "spdx_expression": "NOASSERTION",
                "original_license": pkg.data["licenses"],
                "repository_sources": ["Pypi"],
            }
            deps.append(dep)

        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo

    def package(self, name, **kwargs):
        """
        The package endpoint ignores the name and just returns parsed data
        """
        return self.data.get("package")
