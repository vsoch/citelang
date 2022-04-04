__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import re

from .base import PackagesFromFile


class PythonManager(PackagesFromFile):
    def parse_python_deps(self, lines):
        """
        Shared function for deriving a list of python dependencies from lines
        """
        # Dependencies we parse as pypi packages
        # This should also update the cache and make it easier to retrieve later
        deps = []
        for line in lines:

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
            pkg = self.get_package(package_name, version)

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


class RequirementsManager(PythonManager):

    """
    Packages parsed from a requirements.txt file (so from cran)
    """

    name = "requirements.txt"
    underlying_manager = "pypi"
    project_count = None
    homepage = "pypi.org/"
    color = "#006dad"
    default_language = "Python"
    default_versions = None

    def parse(self, content):
        """
        Parse the self.content (the requirements.txt file)
        """
        repo = self.get_repo()
        lines = content.split("\n")
        deps = self.parse_python_deps(lines)
        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo


class SetupManager(PythonManager):

    """
    Packages parsed from a requirements.txt file (so from cran)
    """

    name = "setup.py"
    underlying_manager = "pypi"
    project_count = None
    homepage = "pypi.org/"
    color = "#006dad"
    default_language = "Python"
    default_versions = None

    def parse(self, content):
        """
        Parse the self.content (the requirements.txt file)
        """
        repo = self.get_repo()

        lines = []
        parsing = False
        for line in content.split("\n"):

            if "setup_requires" in line:
                parsing = True

            # We found the start and end
            if parsing and "[" in line and "]" in line:
                lines.append(line)
                break
            elif parsing and "[" in line:
                lines.append(line)

            elif parsing and "]" in line:
                lines.append(line)
                break
            elif parsing:
                lines.append(line)

        # Clean up lines
        cleaned = []
        for line in lines:
            terms = ["setup_requires" + x for x in [":", " :", "=", " =", ""]]
            for term in terms + ["[", "]", '"', "'"]:
                line = line.replace(term, "")
            parts = line.split(",")
            cleaned += [x.strip() for x in parts if x.strip()]

        deps = self.parse_python_deps(cleaned)
        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo
