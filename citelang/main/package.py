__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.main.packages as packages
from citelang.logger import logger


def get_package(manager, name, version=None, client=None, data=None, use_cache=True):
    """
    Return a package handle for a custom package (defined in citelang) or libraries.io
    """
    # Case 1: a custom manager
    if manager in packages.manager_names:
        return CustomPackage(
            name=name,
            manager=manager,
            version=version,
            client=client,
            data=data,
            use_cache=use_cache,
        )

    # Case 2: libraries.io
    return Package(
        name=name,
        manager=manager,
        version=version,
        client=client,
        data=data,
        use_cache=use_cache,
    )


class PackageBase:
    def __init__(
        self, manager, name, version=None, client=None, data=None, use_cache=True
    ):
        """
        The version can be set explicitly or come from the name.
        """
        self.manager = manager
        self.version = version
        self.parse(name)
        self.data = data or {}
        self.latest = None
        self.set_client(client)
        self.use_cache = use_cache

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[citelang-package]"

    @property
    def cache_name(self):
        return f"package/{self.manager}/{self.name}"

    def set_client(self, client=None):
        """
        A package needs a client controller to make continued calls.
        """
        if not client:
            from .client import Client

            self.client = Client()
        self.client = client

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

    def dependencies(self, return_data=False):
        """
        Retrieve custom package dependencies
        """
        manager = packages.managers[self.manager]()

        # Only will be used if we have a version
        cache_name = f"dependencies/{self.manager}/{self.name}/{self.version}"

        # If we don't have a version, we have to retrieve an update
        if not self.version:
            deps = manager.package(self.name).dependencies()
            return self.client.get_endpoint("dependencies", data=deps)

        result = self.client.get_cache(cache_name)
        if not result or not self.use_cache:
            version = "@%s" % self.version if self.version else ""
            logger.info("Retrieving new result for %s@%s..." % (self.name, version))
            deps = manager.package(self.name).dependencies()
            result = self.client.get_endpoint("dependencies", data=deps)
        else:
            result = self.client.get_endpoint("dependencies", data=result)

        # If cache is enabled, we save the result
        self.client.cache(cache_name, result)

        # Return the wrapped result or raw data
        if return_data:
            return result.data.get("dependencies", [])
        return result

    def info(self):
        """
        Get info for a libraries.io or custom package
        """
        manager = packages.managers[self.manager]()

        # First try retrieving from the cache
        result = self.client.get_cache(self.cache_name)
        if not result or not self.use_cache:
            version = "@%s" % self.version if self.version else ""
            logger.info(
                "Retrieving new result for package %s@%s..." % (self.name, version)
            )
            pkg = manager.package(self.name)
            result = self.client.get_endpoint(
                "package", data=pkg, package_name=self.name, manager=self.manager
            )
        else:
            result = self.client.get_endpoint(
                "package", data=result, package_name=self.name, manager=self.manager
            )

        # If cache is enabled, we save the result
        self.client.cache(self.cache_name, result)
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
        result = self.client.get_cache(cache_name)
        if not result or not self.use_cache:
            logger.info(
                "Retrieving new result for %s@%s dependencies..."
                % (self.name, self.version)
            )
            result = self.client.get_endpoint(
                "dependencies",
                manager=self.manager,
                package_name=self.name,
                version=self.version,
            )
        else:
            result = self.client.get_endpoint("dependencies", data=result)

        # If cache is enabled, we save the result
        self.client.cache(cache_name, result)
        if return_data:
            return result.data.get("dependencies", [])
        return result

    def info(self):
        """
        Get info for a libraries.io package
        """
        result = self.client.get_cache(self.cache_name)
        if not result or not self.use_cache:
            version = "@%s" % self.version if self.version else ""
            logger.info(
                "Retrieving new result for package %s@%s..." % (self.name, version)
            )
            result = self.client.get_endpoint(
                "package",
                manager=self.manager,
                package_name=self.name,
            )
        else:
            result = self.client.get_endpoint(
                "package", data=result, manager=self.manager, package_name=self.name
            )

        # Set a latest version if we find one
        if "versions" in result.data and result.data["versions"]:
            self.latest = result.data["versions"][-1]["number"]
        return result
