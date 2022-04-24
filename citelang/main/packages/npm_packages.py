__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import json

import re

from .base import PackagesFromFile


class NPMPackageManager(PackagesFromFile):
    """
    Packages from a package.json
    """

    name = "package.json"
    underlying_manager = "npm"
    default_language = "JavaScript"
    project_count = None
    homepage = "https://www.npmjs.com/"
    color = "#d54d25"
    default_versions = None

    def parse(self, content, **kwargs):
        """
        Parse the self.content (the packages.json)
        """
        repo = self.get_repo()

        try:
            meta = json.loads(content)
        except:
            meta = {}

        deps = []
        for package_name, version in meta.get("dependencies", {}).items():

            version = re.sub("(\^|<|>|=)", "", version)

            # Always get rid of @ - doesn't seem to get hits
            package_name = package_name.replace("@", "", 1)
            pkg = self.get_package(package_name, version)
            if not package_name:
                continue

            # If we don't have a package, try using start of name
            if not pkg:
                package_name = package_name.split("/")[0]
                pkg = self.get_package(package_name, version)
                if not pkg:
                    continue

            if not pkg or not package_name:
                continue

            # Ensure we have version, fallback to latest
            if not version:
                version = pkg.data["latest_release_number"]

            # Require saving to cache here - many expensive calls
            cache_name = f"package/npm/{package_name}/{version}"
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
                "repository_sources": ["NPM"],
            }
            deps.append(dep)

        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo
