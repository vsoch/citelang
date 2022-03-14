__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.utils as utils
import citelang.main.base as base
import citelang.main.endpoints as endpoints
import citelang.main.result as results
import citelang.main.package as package
from citelang.main.settings import Settings

import time

import os
import json
import requests
import shutil


class Package:
    """
    A basic wrapper for package parsing functions
    """

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

    def set_client(self, client=None):
        """
        A package needs a client controller to make continued calls.
        """
        if not client:
            from .client import Client

            self.client = Client()
        self.client = client

    def dependencies(self, return_data=False):

        # Set version to latest if not defined!
        if not self.version:
            self.info()
            self.version = self.latest

        cache_name = f"dependencies/{self.manager}/{self.name}/{self.version}"
        result = self.client.get_endpoint(
            "dependencies",
            cache_name=cache_name,
            use_cache=self.use_cache,
            manager=self.manager,
            package_name=self.name,
            version=self.version,
        )
        if return_data:
            return result.data.get("dependencies", [])
        return result

    def info(self):
        info = self.client.get_endpoint(
            "package",
            cache_name=self.cache_name,
            package_name=self.name,
            manager=self.manager,
            use_cache=self.use_cache,
        )
        if "versions" in info.data and info.data["versions"]:
            self.latest = info.data["versions"][-1]["number"]
        return info

    @property
    def cache_name(self):
        return f"package/{self.manager}/{self.name}"

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
