__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.utils as utils
import citelang.main.base as base
import citelang.main.result as results
import citelang.main.package as package
import citelang.main.packages as packages
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
        self._update_roots(**kwargs)
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
        table, round_by = self._prepare_table(self.roots)

        # Add listing of packages and dependencies to parser
        self.data = table
        self.round_by = round_by
        return self

    def _prepare_table(self, roots):
        """
        Helper function to prepare the average credit summary table.
        """
        table = {}

        # Multiplier for credit depending on total packages
        splitby = 1 / len(roots)
        for lib, root in roots.items():
            for node in root.iternodes():
                if node.obj.manager not in table:
                    table[node.obj.manager] = {}
                if node.name not in table[node.obj.manager]:
                    table[node.obj.manager][node.name] = {
                        "credit": 0,
                        "url": node.obj.homepage,
                    }
                table[node.obj.manager][node.name]["credit"] += node.credit * splitby
        return table, root.round_by

    def prepare_custom_table(
        self,
        includes,
    ):
        """
        Prepare (and return) a table filtered to a specific kind of root.
        """
        # Multiplier for credit depending on total packages
        roots = {}
        for lib, root in self.roots.items():
            reqfile = lib.split(":")[0]
            if reqfile in includes:
                roots[lib] = root

        table, _ = self._prepare_table(roots)
        return table

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

        # Are we rendering back into the raw content?
        self.rendering_content = True

        super().__init__(*args, **kwargs)
        if filename:
            self.load(filename)
            self.filename = os.path.abspath(filename)

    def load(self, filename):
        if not os.path.exists(filename):
            logger.exit(f"{filename} does not exist")
        self.content = utils.read_file(filename)

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

    def render(self, start_end_blocks=True, data=None):
        """
        Render final file!
        """
        markdown = table_template

        # Allow parsing custom data
        data = data or self.data

        # Sort from least to greatest
        listing = []
        for manager, pkgs in data.items():
            for pkg, meta in pkgs.items():
                listing.append((manager, pkg, meta["credit"], meta["url"]))

        listing = sorted(listing, key=itemgetter(2), reverse=True)
        for (manager, pkg, credit, url) in listing:
            credit = round(credit, self.round_by)
            if credit == 0:
                logger.warning("Rounded credit for %s is 0, skipping." % pkg)
                continue

            # R packages have some "doubled up" urls, by space or newline
            if url:
                if re.search("( |\n)", url):
                    url = re.split("( |\n)", url.strip())[0]
                pkg = "[%s](%s)" % (pkg, url)
            markdown += "|%s|%s|%s|\n" % (
                manager,
                pkg,
                credit,
            )

        if not self.rendering_content:
            content = self.empty_content
        else:
            content = self.content or self.empty_content

        render = []
        lines = content.split("\n")
        while lines:
            line = lines.pop(0)
            if self.start_block in line:
                while self.end_block not in line:
                    line = lines.pop(0)
                # When we get here we have the end block

                if start_end_blocks:
                    render += (
                        [self.start_block]
                        + markdown.split("\n")
                        + [template_suffix, self.end_block]
                    )
                else:
                    render += markdown.split("\n") + [template_suffix]

            else:
                render.append(line)
        return "\n".join(render)


class RequirementsParser(FileNameParser):
    """
    Given one or more requirements files, create packages for summary.
    """

    def __init__(self, filename: str = None, *args, **kwargs):
        super().__init__(filename=filename, *args, **kwargs)

        # We don't want to render back into requirements.txt
        self.rendering_content = False

    def badge(self, name, template="static", filename=None, *args, **kwargs):
        """
        Generate a badge for a requirements file.
        """
        self.gen(filename=filename or self.filename, name=name, *args, **kwargs)
        root = list(self.roots.values())[0]
        if template == "treemap":
            return results.Treemap(root)
        elif template == "sunburst":
            return results.InteractiveBadge(root)
        return results.Badge(root)

    def load_datafiles(self, files, includes=None):
        """
        Given a list of data.json files, load into roots and then generate the table.
        """
        roots = {}

        # Take average depending on number of roots
        splitby = 1 / len(files)
        for filename in files:
            if not os.path.exists(filename):
                logger.warning("%s does not exist, skipping." % filename)
                continue
            data = utils.read_json(filename)
            for manager, libs in data.items():
                if includes and manager not in includes:
                    continue
                if manager not in roots:
                    roots[manager] = {}
                for libname, libmeta in libs.items():
                    if not libname:
                        continue
                    if libname not in roots[manager]:
                        libmeta["credit"] = libmeta["credit"] * splitby
                        roots[manager][libname] = libmeta
                    else:
                        if libmeta["url"] and not roots[manager][libname]["url"]:
                            roots[manager][libname]["url"] = libmeta["url"]
                        roots[manager][libname]["credit"] += libmeta["credit"] * splitby
        return roots

    def gen(self, name, filename=None, *args, **kwargs):
        """
        Add a requirements file. Manager is determined by filename, and name
        is required to label the package.
        """
        if filename is not None:
            self.load(filename)
        else:
            filename = self.filename

        if not self.content:
            logger.exit("no filename provided or filename is empty, nothing to parse.")

        # Do we have a known dependency file?
        basename = os.path.basename(filename)
        pkg = None

        if basename in packages.filesystem_manager_names:
            manager_kwargs = {
                "content": self.content,
                "package_name": name,
                "filename": filename,
            }

            # Custom set the name of the manager
            pkg = package.get_package(
                manager=basename,
                name=name,
                manager_kwargs=manager_kwargs,
            )
            # Populate dependencies and package
            pkg.info()

            uid = "%s:%s" % (basename, filename)
            self.roots[uid] = self._graph(
                manager=pkg.underlying_manager.underlying_manager,
                name=name,
                pkg=pkg,
                **kwargs,
            )

        if not pkg:
            logger.exit(f"Dependency file type {basename} not known, or none found.")

        self.prepare_table()
        return self
