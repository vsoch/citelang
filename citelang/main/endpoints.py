__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import citelang.defaults as defaults
from datetime import datetime
import sys

# Registered endpoints (populated on init)
registry = {}
registry_names = []


class Endpoint:
    dont_truncate = ["url"]
    emoji = "sparkles"

    def __init__(self, *args, **kwargs):
        self.apiroot = defaults.apiroot
        for attr in ["name", "path"]:
            if not hasattr(self, attr):
                sys.exit(
                    "Misconfigured endpoint %s missing %s attribute" % (self, attr)
                )

        # If we have attribute format_url we require the params
        self.format_params(**kwargs)

    def table_data(self, data):
        """
        A custom data parser, optionally if an endpoint needs to parse data further.
        """
        return data

    def format_params(self, **kwargs):
        required = getattr(self, "format_url", [])
        params = {}
        for require in required:
            if require not in kwargs:
                sys.exit(f"parameter {require} is required for this endpoint.")
            params[require] = kwargs[require]

        # If we have parameters, format the path
        if params:
            self.path = self.path.format(**params)
        self.params = params

    # If needed, make sure endpoint data is sorted
    def order(self, data):
        return data

    @property
    def url(self):
        return self.apiroot + self.path

    @property
    def title(self):
        return self.name.capitalize()

    def _get_attribute_or_list(self, name):
        listing = []
        if hasattr(self, name):
            listing = getattr(self, name, []) or []
        return listing

    @property
    def truncate_list(self):
        return self._get_attribute_or_list("dont_truncate")

    @property
    def skip_list(self):
        return self._get_attribute_or_list("skips")


class PackageManagers(Endpoint):
    name = "package_managers"
    path = "/api/platforms"
    emoji = "box"
    skips = ["color"]


class Package(Endpoint):
    name = "package"
    path = "/api/{manager}/{package_name}"
    emoji = "box"
    format_url = ["manager", "package_name"]
    skips = [
        "repository_sources",
        "spdx_expression",
        "researched_at",
        "original_license",
    ]

    def table_data(self, data):
        # package should return a list of versions
        return data.get("versions")

    @property
    def title(self):
        return "Package " + self.params.get("package_name", "")


for endpoint in [PackageManagers, Package]:
    registry_names.append(endpoint.name)
    registry[endpoint.name] = endpoint

registry_names.sort()
