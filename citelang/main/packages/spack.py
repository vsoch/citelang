__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Custom package managers not in libraries IO

import requests
import jsonschema
from .base import PackageManager
import citelang.main.schemas as schemas
from citelang.logger import logger


class SpackManager(PackageManager):
    """
    Packages from spack.
    """

    name = "spack"
    apiroot = "https://spack.github.io/packages/data"
    homepage = "https://spack.github.io/packages"
    color = "#0f3a80"
    default_language = None
    default_versions = []

    @property
    def project_count(self):
        try:  # "pythonic"
            return len(requests.get("%s/packages.json" % self.apiroot).json())
        except:
            return None

    def dependencies(self, name):
        """
        Get dependencies for a spack package

        Some package managers have separate endpoints for this, but we use
        the same package endpoint and return that data.
        """
        if not hasattr(self, "data"):
            self.package(name)
        return self.data

    def package(self, name, **kwargs):
        """
        Get metadata for a spack package. Try to format like libraries.io
        """
        url = "%s/packages/%s.json" % (self.apiroot, name)
        response = requests.get(url)
        if response.status_code != 200:
            logger.exit("There was an issue retrieving %s" % url)

        # The spack meta response already has name, description, homepage, versions
        meta = response.json()
        meta["keywords"] = []
        meta["language"] = None
        meta["versions"] = [{"number": x["name"]} for x in meta["versions"]]

        # Ensure we match schema
        jsonschema.validate(meta, schema=schemas.package)
        self.data = meta
        return meta
