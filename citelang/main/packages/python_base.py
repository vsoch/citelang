__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import re

from .base import PackagesFromFile


class PythonManager(PackagesFromFile):
    underlying_manager = "pypi"
    project_count = None
    homepage = "pypi.org/"
    color = "#006dad"
    default_language = "Python"
    default_versions = None

    def parse_python_deps(self, lines, **kwargs):
        """
        Shared function for deriving a list of python dependencies from lines
        """
        # Dependencies we parse as pypi packages
        # This should also update the cache and make it easier to retrieve later
        deps = []
        for line in lines:

            # Skip local installs with -e
            if "-e" in line:
                continue
            line = line.split("#", 1)[0]

            # skip comments
            if line.strip().startswith("#"):
                continue

            # We can't easily add github pypi references
            if not line or "git@" in line:
                continue

            version = None
            package_name = line.strip()
            if re.search("(==|~=|<=|>=|<|>|!=)", package_name):
                package_name, _, version = re.split(
                    "(==|~=|<=|>=|<|>|!=)", package_name
                )
                version = version.strip()
            package_name = package_name.strip()

            # We cannot parse a dep without a name
            if not package_name:
                continue

            # Remove variants
            package_name = re.sub("\[.+\]", "", package_name)

            # First add requirements (names and pypi manager) to deps
            pkg = self.get_package(package_name, version)
            if not pkg:
                logger.warning("Issue getting package %s, skipping" % package_name)
                continue

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
        return deps
