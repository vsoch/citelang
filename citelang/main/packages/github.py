__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Custom package managers not in libraries IO

import re
import os
import requests
from citelang.logger import logger
import citelang.utils as utils

from .base import PackageManager


def find_dependencies(tmpdir):
    """
    Given a repository root, look for dependency files.
    """
    # TODO here we can clone and look for requirements.txt, etc.
    return []


class GitHubManager(PackageManager):
    """
    Packages from GitHub, either release, or branch.
    """

    name = "github"
    apiroot = "https://api.github.com"
    homepage = "https://github.com"
    color = "#000000"
    default_language = None
    project_count = None
    apiroot = "https://api.github.com"

    def clone(self, name):
        """
        Clone a repository and sniff for dependency files.
        """
        tmpdir = utils.get_tmpdir()
        res = utils.run_command(
            ["git", "clone", "--depth", "1", f"https://github.com/{name}", tmpdir]
        )

        # Don't fail entire process, just can't get dependencies
        if res["return_code"] != 0:
            return
        return tmpdir

    def get_or_fail(self, url, headers):
        """
        Shared endpoint to get a url or fail.
        """
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.exit("Cannot retrieve %s: %s" % (url, response.json()))
        return response.json()

    def package(self, name, **kwargs):

        # Ensure name in right format
        if not re.search("([a-z0-9]+)[/]([a-z0-9]+)", name):
            logger.exit("Please provide a repository in the format <org>/<name")

        headers = {
            "Accept": "application/vnd.github.v3+json;application/vnd.github.antiope-preview+json;application/vnd.github.shadow-cat-preview+json"
        }
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = "token %s" % token
        else:
            logger.warning("Your API requests will be limited without GITHUB_TOKEN")

        repo = self.get_or_fail(f"{self.apiroot}/repos/{name}", headers)

        # TODO add parsing of clones
        # Clone repository to look for dependency files
        # dest = self.clone(name)
        # if dest and os.path.exists(dest):
        #    repo['dependencies'] = find_dependencies(dest)
        #    shutil.rmtree(dest)
        # else:
        repo["dependencies"] = []
        repo["name"] = repo["full_name"]

        # Get versions from releases API
        releases = self.get_or_fail(
            f"{self.apiroot}/repos/{name}/releases?per_page=100", headers
        )
        repo["versions"] = [
            {"published_at": x["published_at"], "number": x["tag_name"]}
            for x in releases
        ]
        if not repo["homepage"]:
            repo["homepage"] = repo["html_url"]
        return repo
