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

    def __init__(self, require_params=False, *args, **kwargs):
        self.apiroot = defaults.apiroot
        for attr in ["name", "path"]:
            if not hasattr(self, attr):
                sys.exit(
                    "Misconfigured endpoint %s missing %s attribute" % (self, attr)
                )

        # If we have attribute format_url we require the params
        if require_params:
            self.require_params(**kwargs)
        else:
            self.format_params(**kwargs)

    def table_data(self, data):
        """
        A custom data parser, optionally if an endpoint needs to parse data further.
        """
        return data

    def require_params(self, **kwargs):
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

    def format_params(self, **params):
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
        return self.name.replace("_", " ").capitalize()

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


class Dependencies(Endpoint):
    name = "dependencies"
    path = "/api/{manager}/{package_name}/{version}/dependencies"
    format_url = ["manager", "package_name", "version"]
    emoji = "arrow"
    skips = ["normalized_licenses"]
    dont_truncate = ["project_name"]

    def table_data(self, data):
        return data.get("dependencies")


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

    def order(self, data):
        """
        Order versions by published at
        """
        versions = data.get("versions", [])
        if versions and "published_at" in versions[0]:
            data["versions"] = sorted(
                versions,
                key=lambda x: datetime.strptime(
                    x["published_at"].split("T", 1)[0], "%Y-%m-%d"
                ),
            )
        elif versions:
            data["versions"] = sorted(
                data["versions"], key=lambda x: x["number"], reverse=True
            )

        return data

    def table_data(self, data):
        # package should return a list of versions
        return data.get("versions")

    @property
    def title(self):
        return "Package " + self.params.get("package_name", "")


for endpoint in [PackageManagers, Package, Dependencies]:
    registry_names.append(endpoint.name)
    registry[endpoint.name] = endpoint

registry_names.sort()
