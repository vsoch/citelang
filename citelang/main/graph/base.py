__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import citelang.utils as utils
from citelang.logger import logger

import secrets
import string
import sys
import os


class GraphBase:
    def __init__(self, target, results, outfile=None):
        self.results = results
        self.uids = {}
        self.symbol_uids = {}
        self.linked_libs = {}
        self.fullpaths = {}
        self.target = target
        self.parse()
        self._outfile = outfile

    @property
    def outfile(self):
        if not self._outfile:
            self._outfile = (
                sys.stdout
            )  # utils.get_tmpfile(prefix="elfcall-", suffix=".txt")
        return self._outfile

    def get_found_imported(self):

        imported = set()

        # filename is the library importing
        for filename, metas in self.organized.items():

            # meta here (lib) is the one exporting e.g., lib -> export -> filename
            for meta in metas:
                symbol = meta["name"]
                typ = meta["type"]
                bind = meta["bind"]
                imported.add((symbol, typ, bind))
        return imported

    def parse(self):
        """
        Organize locations by fullpath and linked libs, and generate placeholder names
        """
        self.organized = {}

        # Create placeholder for the main binary of interest
        self.uids[self.target["name"]] = self.generate_placeholder()

        # And now for linked libs, etc.
        for symbol, meta in self.results.items():
            if meta["lib"]["fullpath"] not in self.organized:
                self.organized[meta["lib"]["fullpath"]] = []
            self.organized[meta["lib"]["fullpath"]].append(meta)
            self.uids[meta["lib"]["fullpath"]] = self.generate_placeholder()
            self.linked_libs[meta["lib"]["fullpath"]] = meta["linked_libs"]

            # We only need fullpaths for linked libs (not from needed) to get fullpath
            basename = os.path.basename(meta["lib"]["fullpath"])
            if (
                basename in self.fullpaths
                and self.fullpaths[basename] != meta["lib"]["fullpath"]
            ):
                logger.warning(
                    "Warning: a library of the same name (and different path) exists, graph output might not be correct."
                )
            self.fullpaths[basename] = meta["lib"]["fullpath"]

        for filename, linked_libs in self.linked_libs.items():
            for linked_lib in linked_libs:
                self.uids[linked_lib] = self.generate_placeholder()

    def generate_placeholder(self):
        """
        Generate a unique placeholder name for a node.
        """
        # Taken from the Python3 documentation:
        # https://docs.python.org/3/library/secrets.html#recipes-and-best-practices
        while True:
            name = "".join(
                secrets.choice(string.ascii_letters) for i in range(8)
            ).lower()
            if name not in self.uids and name not in self.symbol_uids:
                return name

    def iter_linkswith(self):
        """
        Yield filename, fileuid, linked_lib, and linked_lib uid
        """
        # First record that each filename links with our main binary
        for filename, symbols in self.organized.items():
            yield self.target["name"], self.uids[
                self.target["name"]
            ], filename, self.uids[filename]

        # Now Record linked dependencies
        for filename, symbols in self.organized.items():
            for linked_lib in self.linked_libs[filename]:
                if linked_lib in self.fullpaths:
                    linked_lib = self.fullpaths[linked_lib]
                yield filename, self.uids[filename], linked_lib, self.uids[linked_lib]

    def iter_needed(self):
        """
        Yield binary name, uid, symbol name, symbol uid
        """
        for symbol in self.target["imported"]:
            placeholder = self.symbol_uids[symbol]
            yield self.target["name"], self.uids[
                self.target["name"]
            ], symbol, placeholder

    def iter_exports(self):
        """
        Return a list of filename, uid, symbol, and symbol uid
        """
        # Now add symbols for linked dependences
        for filename, symbols in self.organized.items():
            for symbol in symbols:
                if symbol["name"] not in self.symbol_uids:
                    self.symbol_uids[symbol["name"]] = self.generate_placeholder()
                placeholder = self.symbol_uids[symbol["name"]]
                yield filename, self.uids[filename], symbol["name"], placeholder

    def iter_symbols(self):
        """
        Iterate over symbols and return uid, name, label, and type (if exists)
        """
        results = set()

        # Found symbols plus needed imported (not necessarily all are found)
        imported = self.get_found_imported()

        # Create a node for each symbol
        seen = set()
        for symbol in imported:
            placeholder = self.generate_placeholder()
            self.symbol_uids[symbol[0]] = placeholder
            results.add((placeholder, symbol[0], symbol[0], symbol[1]))
            seen.add(symbol[0])

        # TODO need to fix this so symbols imported have name and type
        for symbol in self.target["imported"]:
            if symbol in seen:
                continue
            placeholder = self.generate_placeholder()
            self.symbol_uids[symbol] = placeholder
            results.add((placeholder, symbol, symbol, None))
        for result in results:
            yield result[0], result[1], result[2], result[3]

    def iter_elf(self):
        """Iterate the uid, name and label for the main binary and libs"""
        results = []
        results.append(
            (
                self.uids[self.target["name"]],
                os.path.basename(self.target["name"]),
                os.path.basename(self.target["name"]),
            )
        )

        # Create elf for main files and those linked to
        seen_libs = set()
        seen_libs.add(self.target["name"])
        for filename, symbols in self.organized.items():
            if os.path.basename(filename) in self.fullpaths:
                filename = self.fullpaths[os.path.basename(filename)]
            if filename not in seen_libs:
                results.append(
                    (
                        self.uids[filename],
                        os.path.basename(filename),
                        os.path.basename(filename),
                    )
                )
                seen_libs.add(filename)

            # Now Record linked dependencies
            for linked_lib in self.linked_libs[filename]:

                # linked_libs often are just the basename, but we don't want to add twice
                # so we store the fullpaths here to resolve to fullpath
                if linked_lib in self.fullpaths:
                    linked_lib = self.fullpaths[linked_lib]
                if linked_lib in seen_libs:
                    continue
                seen_libs.add(linked_lib)
                results.append(
                    (
                        self.uids[linked_lib],
                        os.path.basename(linked_lib),
                        os.path.basename(linked_lib),
                    )
                )
                seen_libs.add(linked_lib)

        for result in results:
            yield result[0], result[1], result[2]
