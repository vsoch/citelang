__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.defaults as defaults
import citelang.utils as utils
import citelang.main.endpoints as endpoints
import citelang.main.table as table
from citelang.main.settings import Settings

from copy import deepcopy
import time

import os
import json
import requests


class Client:
    """
    Interact with a libaries.io server via CiteLang
    """

    def __init__(self, settings_file=None, validate=True, quiet=False):
        self.quiet = quiet
        self.session = requests.session()
        self.headers = {"Accept": "application/json", "User-Agent": "citelang-python"}
        self.params = {"per_page": 100}
        self.getenv()

        # keep a cache of data for a session
        self._cache = {}

        # If we don't have default settings, load
        if not hasattr(self, "settings"):
            self.settings = Settings(settings_file, validate=validate)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[citelang-client]"

    def getenv(self):
        """
        Get any token / username set in the environment
        """
        self.api_key = os.environ.get("CITELANG_LIBRARIES_KEY")
        if self.api_key:
            self.params.update({"api_key": self.api_key})

    def cache(self, name, result):
        """
        Given a result, cache if the user has cache enabled.
        """
        if self.settings.disable_cache == True:
            return

        # If we are using the memory cache, return from there.
        if not self.settings.disable_memory_cache:
            if name in self._cache:
                return self._cache[name]

        # Ensure cache directory exists
        utils.mkdir_p(self.settings.cache_dir)

        # prepare the path (e.g., cache_dir/package_managers.json)
        path = self.get_cache_name(name)

        # Don't write empty data
        if not result.data:
            logger.warning("No data found for result, not writing %s" % path)
            return

        # If we are using the memory cache, save to it
        if not self.settings.disable_memory_cache:
            self._cache[name] = result.data

        # We can't predict nesting, so always make directory
        utils.mkdir_p(os.path.dirname(path))
        utils.write_json(result.data, path)

    def get_cache_name(self, name):
        """
        Return a json cache entry.
        """
        return os.path.join(self.settings.cache_dir, "%s.json" % name)

    def get_cache(self, name, endpoint=None):
        """
        Given a cache name (typically matching the endpoint) retrieve if exists.
        If provided and endpoint, wrap the result with the endpoint. Otherwise,
        return the json result.
        """
        path = self.get_cache_name(name)
        if not os.path.exists(path):
            return

        # Load the cache, return as a result if it exists.
        data = utils.read_json(path)
        if data and endpoint:
            return table.Result(data, endpoint)
        elif data:
            return data

    def get_endpoint(self, name, use_cache=True, cache_name=None, **kwargs):
        """
        Get a named endpoint, optionally, using the cache (default)
        """
        if name not in endpoints.registry:
            names = endpoints.registry_names
            sys.exit(f"{name} is not a known endpoint. Choose from {names}")

        # Create the endpoint with any optional params
        endpoint = endpoints.registry[name](**kwargs)

        # First shot try to use cache OR not if disabled
        result = self.get_cache(cache_name or name, endpoint)
        if not result or not use_cache:
            result = table.Result(self.get(endpoint.url), endpoint)

        # If cache is enabled, we save the result
        self.cache(cache_name or name, result)
        return result

    def check_manager(self, name, use_cache=True):
        """
        Ensure a package manager name is valid before attempting to query.
        """
        managers = self.get_endpoint("package_managers", use_cache=use_cache)

        # Ensure the manager is allowed
        if managers.data:
            managers = [x["name"].lower() for x in managers.data]
            if name not in managers:
                managers = "\n".join(managers)
                logger.exit(f"{name} is not a known manager. Choices are:\n{managers}")

    def package_managers(self, use_cache=True):
        """
        Get a listing of package managers supported on libraries.io
        """
        return self.get_endpoint("package_managers", use_cache=use_cache)

    def package(self, manager, name, use_cache=True):
        """
        Lookup a package in a specific package manager
        """
        # Ensure we know the manager before
        # Store package in cache based on manager and name
        cache_name = f"package/{manager}/{name}"
        self.check_manager(manager, use_cache)
        return self.get_endpoint(
            "package",
            cache_name=cache_name,
            package_name=name,
            manager=manager,
            use_cache=use_cache,
        )

    def check_response(self, typ, r, return_json=True, stream=False, retry=True):
        """
        Ensure the response status code is 20x
        """
        # Rate is 60/minute
        if r.status_code == 429:
            logger.info("Exceeded API limit, sleeping 1 minute.")
            time.sleep(60)
            r = self.session.send(r.request)
            return self.check_response(typ, r, return_json, stream, retry=retry)

        if r.status_code == 401:
            logger.exit("You must set CITELAG_LIBRARIES_KEY in the environment.")

        if r.status_code not in [200, 201]:
            logger.exit("Unsuccessful response: %s, %s" % (r.status_code, r.reason))

        # All data is typically json
        if return_json and not stream:
            return r.json()
        return r

    def set_header(self, name, value):
        """
        Set a header, name and value pair
        """
        self.headers.update({name: value})

    def print_response(self, r):
        """
        Print the result of a response
        """
        response = r.json()
        logger.info("%s: %s" % (r.url, json.dumps(response, indent=4)))

    def info(self):
        """
        Get basic server information
        """
        return self.get("/")

    def do_request(
        self,
        typ,
        url,
        data=None,
        json=None,
        headers=None,
        return_json=True,
        stream=False,
    ):
        """
        Do a request (get, post, etc)
        """
        # If we have a cached token, use it!
        headers = headers or {}
        headers.update(self.headers)

        if not self.quiet:
            logger.info("%s %s" % (typ.upper(), url))

        # The first post when you upload the model defines the flavor (regression)
        if json:
            r = requests.request(typ, url, json=json, headers=headers, stream=stream)
        else:
            r = requests.request(typ, url, data=data, headers=headers, stream=stream)
        if not self.quiet and not stream and not return_json:
            self.print_response(r)
        return self.check_response(typ, r, return_json=return_json, stream=stream)

    def post(self, url, data=None, json=None, headers=None, return_json=True):
        """
        Perform a POST request
        """
        return self.do_request(
            "post", url, data=data, json=json, headers=headers, return_json=return_json
        )

    def delete(self, url, data=None, json=None, headers=None, return_json=True):
        """
        Perform a DELETE request
        """
        return self.do_request(
            "delete",
            url,
            data=data,
            json=json,
            headers=headers,
            return_json=return_json,
        )

    def get(
        self, url, data=None, json=None, headers=None, return_json=True, stream=False
    ):
        """
        Perform a GET request
        """
        return self.do_request(
            "get",
            url,
            data=data,
            json=json,
            headers=headers,
            return_json=return_json,
            stream=stream,
        )
