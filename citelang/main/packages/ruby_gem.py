__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from .base import PackagesFromFile
import re


class GemfileManager(PackagesFromFile):
    """
    Packages from a ruby Gemfile
    """

    name = "Gemfile"
    underlying_manager = "rubygems"
    default_language = "ruby"
    project_count = None
    homepage = "https://rubygems.org/"
    color = "#e9573f"
    default_versions = None

    def parse(self, content, **kwargs):
        """
        Parse the self.content (the Gemfile)
        """
        repo = self.get_repo()
        libs = []

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("gem") and "source" not in line:
                for sub in ["gem", "'", '"', ","]:
                    line = line.replace(sub, "").strip()

                for sep in [" if ", ":platforms", ":require"]:
                    line = line.split(sep)[0]

                # Do we have a version?
                if re.search("(~>|@|<=|>=)", line):
                    line, _, version = re.split("(~>|@|<=|>=)", line)
                    line = "%s@%s" % (line.strip(), version.strip())
                libs.append(line)

        deps = []
        for package_name in libs:
            version = None
            if "@" in package_name:
                package_name, version = package_name.split("@", 1)
            elif " " in package_name:
                package_name, version = package_name.split(" ", 1)

            pkg = self.get_package(package_name, version)
            if not pkg:
                continue

            # Ensure we have version, fallback to latest
            if not version:
                version = pkg.data["latest_release_number"]

            # Require saving to cache here - many expensive calls
            cache_name = f"package/rubygems/{package_name}/{version}"
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
                "repository_sources": ["Rubygems"],
            }
            deps.append(dep)

        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo
