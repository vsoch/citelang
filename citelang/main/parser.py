__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.utils as utils
import citelang.main.base as base
import citelang.main.package as package
from operator import itemgetter

import re
import os

table_template = """|Manager|Name|Credit|
|-------|----|------|
"""

template_suffix = "\n> Note that credit values are rounded and expanded (so shared dependencies are represented as one record) and may not add to 1.0. Rounded values that hit zero are removed.\n"

citation_regex = "\@([a-zA-Z0-9]+)\{(.*?)\}"


class Parser(base.BaseClient):
    """
    A parser reads in a markdown file, finds software references, and generates
    a software graph per the user preferences.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}
        self.libs = []
        self.round_by = 3
        self.roots = {}

    def gen(self, name, manager, *args, **kwargs):
        """
        Generate a one off credit table for a named library
        """
        # Prepare a parser that can generate a table
        self.add_lib(name=name, manager=manager)
        self._update_roots()
        self.prepare_table()
        return self

    def parse(self, **kwargs):
        """
        A parser is specific to a base class.
        """
        raise NotImplementedError

    def _update_roots(self, **kwargs):
        """
        Update roots for new libraries we've found
        """
        for lib in self.libs:
            if "name" not in lib or "manager" not in lib:
                logger.warning("Skipping %s, missing name or manager." % lib)
            uid = "%s:%s" % (lib["manager"], lib["name"])

            # Don't generate roots we've already parsed
            if uid in self.roots:
                continue

            if "version" in lib or "release" in lib:
                version = lib.get("version") or lib.get("release")
                uid = "%s@%s" % (uid, version)
                lib["name"] = "%s@%s" % (lib["name"], version)
            self.roots[uid] = self._graph(
                manager=lib["manager"], name=lib["name"], **kwargs
            )

    def prepare_table(self, *args, **kwargs):
        """
        Given a package name and manager, generate roots and a table
        """
        # Generate the table with multiple roots - flatten out credit
        table = {}

        # Multiplier for credit depending on total packages
        splitby = 1 / len(self.roots)
        for lib, root in self.roots.items():
            manager = lib.split(":")[0]
            for node in root.iternodes():
                if manager not in table:
                    table[manager] = {}
                if node.name not in table[manager]:
                    table[manager][node.name] = {
                        "credit": 0,
                        "url": node.obj.homepage,
                    }
                table[manager][node.name]["credit"] += node.credit * splitby

        # Add listing of packages and dependencies to parser
        self.data = table
        self.round_by = root.round_by
        return self

    def add_lib(self, manager, name, **args):
        """
        Manually add a library (e.g., not reading from a pre-existing file)
        """
        self.libs.append({"manager": manager, "name": name, **args})


class FileNameParser(Parser):
    """
    FileNameParser is an abstract parser for one that requires an input filename.
    """

    def __init__(self, filename: str = None, *args, **kwargs):
        self.filename = None
        self.content = None
        super().__init__(*args, **kwargs)
        if filename:
            self.filename = os.path.abspath(filename)
            if not os.path.exists(self.filename):
                logger.exit(f"{filename} does not exist")
            self.content = utils.read_file(self.filename)


class RequirementsParser(FileNameParser):
    """
    Given one or more requirements files, create packages for summary.
    """

    def gen(self, name, *args, **kwargs):
        """
        Add a requirements file. Manager is determined by filename, and name
        is required to label the package.
        """
        if not self.content:
            logger.exit("no filename provided or filename is empty, nothing to parse.")

        # Do we have a known dependency file?
        basename = os.path.basename(self.filename)
        pkg = None
        if basename == "requirements.txt":
            manager_kwargs = {
                "content": self.content,
                "package_name": name,
                "client": self,
            }

            pkg = package.get_package(
                manager="requirements.txt",
                name=name,
                manager_kwargs=manager_kwargs,
                client=self,
            )

            uid = "requirements.txt:%s" % self.filename
            self.roots[uid] = self._graph(
                manager="requirements.txt", name=name, pkg=pkg, **kwargs
            )

        if not pkg:
            logger.exit(f"Dependency file type {basename} not known, or none found.")

        self.prepare_table()
        return self


class MarkdownParser(FileNameParser):
    """
    A markdown parser reads in a markdown file, finds software references
    and generates a software graph per the user preferences.
    """

    @property
    def start_block(self):
        return "<!--citelang start-->"

    @property
    def end_block(self):
        return "<!--citelang end-->"

    @property
    def empty_content(self):
        return """# Software Credit

<!--citelang start-->
<!--citelang end-->

- Generated by [CiteLang](https://github.com/vsoch/citelang)
"""

    def check(self):
        """
        Checks for citelang.
        """
        if self.start_block not in self.content:
            logger.exit(
                "Cannot find %s, ensure it is present where you want the citelang table."
                % self.start_block
            )
        if self.end_block not in self.content:
            logger.exit(
                "Cannot find %s, ensure it is present where you want the citelang table."
                % self.end_block
            )

    def parse(self, **kwargs):
        """
        Given a markdown file, return a list of parse packages and versions.
        """
        self.check()
        for match in re.findall(citation_regex, self.content):
            if len(match) != 2:
                logger.warning(
                    "found malformed citation reference %s, skipping." % match
                )
                continue
            args = {
                y[0]: y[1]
                for y in [x.strip().split("=") for x in match[-1].split(",")]
                if len(y) == 2
            }
            self.libs.append({"manager": match[0], **args})

        # Generate roots from the libraries we have
        self._update_roots(**kwargs)
        return self.prepare_table()

    def render(self):
        """
        Render final file!
        """
        markdown = table_template

        # Sort from least to greatest
        listing = []
        for manager, packages in self.data.items():
            for pkg, meta in packages.items():
                listing.append((manager, pkg, meta["credit"], meta["url"]))

        listing = sorted(listing, key=itemgetter(2), reverse=True)
        for (manager, pkg, credit, url) in listing:
            credit = round(credit, self.round_by)
            if credit == 0:
                logger.warning("Rounded credit for %s is 0, skipping." % pkg)
                continue
            if url:
                pkg = "[%s](%s)" % (pkg, url)
            markdown += "|%s|%s|%s|\n" % (
                manager,
                pkg,
                credit,
            )

        self.content = self.content or self.empty_content
        render = []
        lines = self.content.split("\n")
        while lines:
            line = lines.pop(0)
            if self.start_block in line:
                while self.end_block not in line:
                    line = lines.pop(0)
                # When we get here we have the end block
                render += (
                    [self.start_block]
                    + markdown.split("\n")
                    + [template_suffix, self.end_block]
                )
            else:
                render.append(line)
        return "\n".join(render)
