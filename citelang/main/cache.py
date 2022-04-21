__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.utils as utils
import citelang.main.result as results
import citelang.main.settings as settings

import os
import shutil


class Cache:
    """
    The cache controls saving and loading citelang package content. We should
    be able to load (and use) a cache anywhere.
    """

    _cache = {}

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[citelang-cache]"

    def clear(self, force=False):
        """
        Clear the cache (with confirmation).
        """
        if not force and not utils.confirm_action(
            "Are you sure you want to clear the cache? "
        ):
            return
        if os.path.exists(settings.cfg.cache_dir):
            shutil.rmtree(settings.cfg.cache_dir)

    def set(self, name, result):
        """
        Given a result, cache if the user has cache enabled.
        """
        if settings.cfg.disable_cache == True:
            return

        # If we are using the memory cache, return from there.
        if not settings.cfg.disable_memory_cache:
            if name not in self._cache:
                self._cache[name] = result.data

            # If we end in a version, add to cache too
            # E.g., package/pypi/numpy/1.22.3
            if name.count("/") == 3:
                without_version = name.rsplit("/", 1)[0]
                self._cache[without_version] = result.data

        # Ensure cache directory exists
        utils.mkdir_p(settings.cfg.cache_dir)

        # prepare the path (e.g., cache_dir/package_managers.json)
        path = self.get_cache_name(name)

        # Don't write empty data
        if not result.data:
            logger.warning("No data found for result, not writing %s" % path)
            return

        # If we are using the memory cache, save to it
        if not settings.cfg.disable_memory_cache:
            self._cache[name] = result.data

        # We can't predict nesting, so always make directory
        utils.mkdir_p(os.path.dirname(path))
        utils.write_json(result.data, path)

    def get_cache_name(self, name):
        """
        Return a json cache entry.
        """
        return os.path.join(settings.cfg.cache_dir, "%s.json" % name)

    def is_empty(self, name):
        """
        Given a package name, determine if it's empty (the endpoint tried and
        no result) so we don't try again.
        """
        empty_name = os.path.join(settings.cfg.cache_dir, "%s.empty" % name)
        return os.path.exists(empty_name)

    def mark_empty(self, name):
        """
        Given a package name, mark it empty to indicate the manager doesn't
        have it.
        """
        empty_name = os.path.join(settings.cfg.cache_dir, "%s.empty" % name)
        utils.write_file("", empty_name)

    def get(self, name, endpoint=None):
        """
        Given a cache name (typically matching the endpoint) retrieve if exists.
        If provided and endpoint, wrap the result with the endpoint. Otherwise,
        return the json result.
        """
        # First effort - get from memory
        if name in self._cache:
            return self._cache[name]

        # Now look for filesystem
        path = self.get_cache_name(name)
        if not os.path.exists(path):
            return

        # Load the cache, return as a result if it exists.
        # If there is an error loading it, assume corrupt (and regnerate)
        data = None
        try:
            data = utils.read_json(path)
        except:
            logger.warning(f"Cache entry {path} has corrupt json, removing.")
            os.remove(path)

        if data and endpoint:
            return results.Table(data, endpoint)
        elif data:
            return data


def init_cache():
    return Cache()


cache = init_cache()
