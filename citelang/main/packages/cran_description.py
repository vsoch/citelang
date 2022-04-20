__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import re

from citelang.logger import logger
from .base import PackagesFromFile


class RPackageManager(PackagesFromFile):
    """
    Packages from an R DESCRIPTION file, meaning an R package
    """

    name = "DESCRIPTION"
    underlying_manager = "cran"
    default_language = "R"
    project_count = None
    homepage = "https://cran.r-project.org/"
    color = "#006dad"
    default_versions = None

    def parse(self, content):
        """
        Parse the self.content (the DESCRIPTION file)
        """
        repo = self.get_repo()

        libs = []
        parsing = False
        for line in content.split("\n"):
            # If we are parsing, but hit the end of the list
            if parsing and not line.startswith(" "):
                break
            elif parsing:
                libs.append(line.replace(",", "").strip())
            elif "Imports:" in line:
                parsing = True

        deps = []
        for line in libs:
            version = None
            package_name = None
            if re.search("(==|<=|>=)", line):
                line = line.replace(")", "").replace("(", "")
                package_name, _, version = re.split("(==|<=|>=)", line)
                package_name = package_name.strip()
                version = version.strip()
            else:
                package_name = line

            # We cannot parse a dep without a name
            if not package_name:
                continue

            # Try to get from cache - either versioned or not
            pkg = self.get_package(package_name, version)
            if not pkg:
                logger.warning(f"Cannot find package {package_name}")
                continue

            # Ensure we have version, fallback to latest
            if not version:
                version = pkg.data["latest_release_number"]

            # Require saving to cache here - many expensive calls
            cache_name = f"package/cran/{package_name}/{version}"
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
                "repository_sources": ["Cran"],
            }
            deps.append(dep)

        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo
