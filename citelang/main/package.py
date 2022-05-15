__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.main.packages as packages
import citelang.main.endpoints as endpoints
import citelang.main.cache as cache
from citelang.logger import logger


def get_package(
    manager,
    name,
    version=None,
    data=None,
    use_cache=True,
    manager_kwargs=None,
):
    """
    Return a package handle for a custom package (defined in citelang) or libraries.io
    """
    # Custom kwargs for the manager
    manager_kwargs = manager_kwargs or {}

    # Case 1: a package manager provided by citelang
    if manager in packages.manager_names:
        return CustomPackage(
            name=name,
            manager=manager,
            version=version,
            data=data,
            use_cache=use_cache,
            manager_kwargs=manager_kwargs,
        )

    # Case 2: libraries.io
    return Package(
        name=name,
        manager=manager,
        version=version,
        data=data,
        use_cache=use_cache,
    )


class PackageBase:
    def __init__(
        self,
        manager,
        name,
        version=None,
        data=None,
        use_cache=True,
        manager_kwargs=None,
    ):
        """
        The version can be set explicitly or come from the name.
        """
        self.manager = manager
        self.version = version
        self.parse(name)
        self.data = data or {}
        self.latest = None
        self.use_cache = use_cache
        self.cache = cache.cache
        self.manager_kwargs = manager_kwargs or {}
        self.underlying_manager = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[citelang-package]"

    @property
    def cache_name(self):
        return f"package/{self.manager}/{self.name}"

    @property
    def homepage(self):
        url = self.data.get("package", {}).get("homepage")
        if not url and self.manager == "pypi":
            return f"https://pypi.org/project/{self.name}"
        if not url and self.manager == "go":
            return f"https://{self.name}"
        # Some R urls have TWO and they are wonky
        if url and " " in url:
            url = url.strip().split(" ")[0]
        return url

    def parse(self, name):
        """
        Parse a manager and name into the package
        """
        if "@" in name:
            name, version = name.split("@", 1)
            self.version = version
        if "[" in name and "]" in name:
            name = name.split("[", 1)[0]

        # invalid characters found!
        name = name.replace(";", "")
        self.name = name

    def dependencies(self, return_data=False):
        raise NotImplementedError

    def info(self):
        raise NotImplementedError


class CustomPackage(PackageBase):
    """
    A wrapper for a custom package (provided by citelang)
    """

    def __init__(
        self,
        manager,
        name,
        version=None,
        data=None,
        use_cache=True,
        manager_kwargs=None,
    ):
        super().__init__(manager, name, version, data, use_cache, manager_kwargs)
        if not self.underlying_manager:
            self.underlying_manager = packages.managers[self.manager](
                **self.manager_kwargs
            )

    @property
    def homepage(self):
        url = self.data.get("homepage") or self.data.get("package", {}).get("homepage")
        if not url and self.manager == "github":
            return f"https://github.com/{self.name}"
        if not url and self.manager in ["go.mod", "go"]:
            return f"https://{self.name}"
        if url and " " in url:
            url = url.strip().split(" ")[0]
        return url

    def dependencies(self, return_data=False):
        """
        Retrieve custom package dependencies
        """
        manager = self.underlying_manager

        # Use manager cache first
        if "dependencies" in manager.data:
            return manager.data["dependencies"]

        cache_name = None
        result = None

        # If we aren't given a version, look for default branches
        if not self.version and manager.default_versions and self.use_cache:
            for version in manager.default_versions:
                cache_name = f"package/{self.manager}/{self.name}/{version}"
                result = self.cache.get(cache_name)
                if result:
                    result = endpoints.get_endpoint("dependencies", data=result)
                    self.version = version
                    break

        # If we don't have a version, we have to retrieve an update
        if not result and not self.version:
            deps = manager.package(self.name)
            result = endpoints.get_endpoint("dependencies", data=deps)
            self.version = result.data.get("default_version")
            cache_name = f"package/{self.manager}/{self.name}/{self.version}"

        # We have a version, either retrieve from cache or anew
        elif not result and self.version:
            cache_name = f"package/{self.manager}/{self.name}/{self.version}"
            result = self.cache.get(cache_name)
            if not result or not self.use_cache:
                version = "@%s" % self.version if self.version else ""
                logger.info("Retrieving new result for %s%s..." % (self.name, version))
                deps = manager.package(self.name)
                result = endpoints.get_endpoint("dependencies", data=deps)
            elif result:
                result = endpoints.get_endpoint("dependencies", data=result)

        # If cache is enabled, we save the result
        if result and cache_name:
            self.cache.set(cache_name, result)

        # Return the wrapped result or raw data
        deps = result.data.get("dependencies", [])
        self.data["package"] = result.data
        self.data["dependencies"] = deps
        if return_data:
            return deps
        return result

    def info(self):
        """
        Get info for a custom package
        """
        manager = self.underlying_manager

        # Use manager cache first
        if "package" in manager.data:
            return manager.data["package"]

        # First try retrieving from the cache
        result = self.cache.get(self.cache_name)
        if not result or not self.use_cache:
            version = "@%s" % self.version if self.version else ""
            logger.info(
                "Retrieving new result for package %s%s..." % (self.name, version)
            )
            pkg = manager.package(self.name)
            result = endpoints.get_endpoint(
                "package", data=pkg, package_name=self.name, manager=self.manager
            )
        else:
            result = endpoints.get_endpoint(
                "package", data=result, package_name=self.name, manager=self.manager
            )

        # If cache is enabled, we save the result
        self.cache.set(self.cache_name, result)
        self.data["package"] = result.data
        return result


class Package(PackageBase):
    """
    A basic wrapper for package parsing functions (libraries.io)
    """

    def dependencies(self, return_data=False):
        """
        Retrieve libraries.io dependencies
        """
        if not self.version:
            self.info()
            self.version = self.latest

        # Check for result in cache
        cache_name = f"dependencies/{self.manager}/{self.name}/{self.version}"
        result = self.cache.get(cache_name)
        if not result or not self.use_cache:
            logger.info(
                "Retrieving new result for %s@%s dependencies..."
                % (self.name, self.version)
            )
            result = endpoints.get_endpoint(
                "dependencies",
                manager=self.manager,
                package_name=self.name,
                version=self.version,
            )
        else:
            result = endpoints.get_endpoint("dependencies", data=result)

        # If cache is enabled, we save the result
        self.cache.set(cache_name, result)
        deps = result.data.get("dependencies", [])
        self.data["dependencies"] = deps
        if return_data:
            return deps
        return result

    def info(self):
        """
        Get info for a libraries.io package
        """
        result = self.cache.get(self.cache_name)
        if not result and not self.manager:
            return result

        if not result or not self.use_cache:
            version = "@%s" % self.version if self.version else ""
            logger.info(
                "Retrieving new result for package %s%s..." % (self.name, version)
            )
            result = endpoints.get_endpoint(
                "package",
                manager=self.manager,
                package_name=self.name,
            )
        else:
            result = endpoints.get_endpoint(
                "package", data=result, manager=self.manager, package_name=self.name
            )

        # Set a latest version if we find one
        if "versions" in result.data and result.data["versions"]:
            self.latest = result.data["versions"][-1]["number"]
        self.cache.set(self.cache_name, result)
        self.data["package"] = result.data
        return result
