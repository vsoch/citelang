__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
from .base import PackagesFromFile


class CMakeListManager(PackagesFromFile):
    """
    Packages from a CMakeLists.txt
    """

    name = "CMakeLists.txt"

    # We use spack because we can probably find a lot of C++ deps here!
    underlying_manager = "spack"
    default_language = "C++"
    project_count = None
    homepage = None
    color = "#e9573f"
    default_versions = None

    def parse(self, content, **kwargs):
        """
        Attempt to parse the CMakeList.txt file. This can give us at least
        one level of dependencies.
        """
        repo = self.get_repo()
        libs = []

        for line in content.split("\n"):
            line = line.strip()

            # A version could be here as second item...
            if "find_package" in line:
                lib = line.split("(")[1].split(" ")[0].strip().replace(")", "")
                if not lib:
                    continue
                logger.info(f"Found lib {lib}")
                libs.append(lib.lower())

            elif "cmake_minimum_required" in line:
                version = line.split("(")[1].split(" ")[1].strip(")").strip()
                libs.append(f"cmake@{version}")

            elif "set(PROJECT_VERSION" in line:
                version = (
                    line.split(" ")[1]
                    .split(" ")[0]
                    .replace(")", "")
                    .replace('"', "")
                    .replace("'", "")
                )
                repo["versions"][0]["number"] = version

            elif "project" in line:
                repo["name"] = line.split("(")[1].split(" ")[0].strip()

        deps = []
        for package_name in libs:
            version = None
            if "@" in package_name:
                package_name, version = package_name.split("@", 1)

            # use latest release version. This will be wrong for an old
            # dependency, but it's not worth it to make a ton of extra API calls
            dep = {
                "name": package_name,
                "project_name": package_name,
                "number": version,
                "published_at": repo["versions"][0]["published_at"],
                "researched_at": None,
                "spdx_expression": "NOASSERTION",
                "original_license": None,
                "repository_sources": ["Cpp"],
            }
            deps.append(dep)

        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo
