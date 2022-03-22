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


def find_dependencies(repo):
    """
    Given a repository root, look for dependency files. We could use the GraphQL
    library, but this REQUIRES a GitHub token, which is kind of annoying. For now
    we are trying to scrape them :)
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.exit(
            "You need beautiful soup in order to get GitHub dependencies. pip install bs4"
        )

    url = "https://github.com/{}/network/dependencies".format(repo)

    repos = set()
    while url is not None:
        response = requests.get(url)
        if response.status_code != 200:
            logger.warning("Issue getting dependencies for %s" % repo)
            return [{"name": x} for x in sorted(list(repos))]
        soup = BeautifulSoup(response.content, "html.parser")

        for t in soup.findAll("div", {"class": "Box-row"}):
            repo = t.find("a", {"data-hovercard-type": "repository"})
            if repo:
                repo = repo.text.replace(" ", "").strip()
                repos.add(repo)

        # Do we have pagination?
        pagination = soup.find("div", {"class": "paginate-container"})
        url = None
        if pagination:
            pagination_a = pagination.find("a")
            if pagination_a:
                url = pagination_a["href"]

    # Ensure dependencies come with homepage
    return [
        {"name": x, "homepage": "https://github.com/%s" % x}
        for x in sorted(list(repos))
    ]


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
    default_versions = ["main", "master", "develop"]

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

        # Parse repos dependency page. This includes deps for CI too.
        repo["dependencies"] = find_dependencies(name)
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
