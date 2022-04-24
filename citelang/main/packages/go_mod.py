__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from .base import PackagesFromFile


class GoModuleManager(PackagesFromFile):
    """
    Packages from a go module file
    """

    name = "go.mod"
    underlying_manager = "go"
    default_language = "Go"
    project_count = None
    homepage = "https://go.dev/"
    color = "#007d9c"
    default_versions = None

    def parse(self, content, **kwargs):
        """
        Parse the self.content (the Gemfile)
        """
        repo = self.get_repo()

        libs = []
        parsing = False
        for line in content.split("\n"):
            if "require (" in line:
                parsing = True
                continue
            if parsing and ")" in line:
                break
            if parsing:
                line = line.strip()

                # Get rid of comments
                line = line.split("//")[0].strip()
                libs.append(line)

        deps = []
        for package_name in libs:
            version = None
            if " " in package_name:
                package_name, version = package_name.split(" ", 1)

            # Many go packages are not known
            pkg = None
            try:
                pkg = self.get_package(package_name, version)
            except:
                pass

            if pkg is None:
                dep = {
                    "name": package_name,
                    "project_name": package_name,
                    "number": version,
                    "published_at": None,
                    "researched_at": None,
                    "spdx_expression": "NOASSERTION",
                    "original_license": None,
                    "repository_sources": ["Unknown"],
                }
                deps.append(dep)
                continue

            # Ensure we have version, fallback to latest
            if not version:
                version = dep.data["latest_release_number"]

            # Require saving to cache here - many expensive calls
            cache_name = f"package/go/{package_name}/{version}"
            self.cache.set(cache_name, pkg)

            # use latest release version. This will be wrong for an old
            # dependency, but it's not worth it to make a ton of extra API calls
            dep = {
                "name": package_name,
                "project_name": package_name,
                "number": version,
                "published_at": dep.data["latest_stable_release_published_at"],
                "researched_at": None,
                "spdx_expression": "NOASSERTION",
                "original_license": pkg.data["licenses"],
                "repository_sources": ["Go"],
            }
            deps.append(dep)

        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo
