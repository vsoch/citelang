__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import secrets
import string
import sys


class GraphBase:
    def __init__(self, data, outfile=None):
        self.data = data
        self.uids = {}
        self.deps_ids = {}
        self.parse()
        self._outfile = outfile

    @property
    def outfile(self):
        if not self._outfile:
            self._outfile = sys.stdout
        return self._outfile

    def parse(self):
        """
        Create a flattened list of dependency names, and generate placeholder names
        """
        next_nodes = [self.data]
        while next_nodes:
            next_node = next_nodes.pop(0)
            if next_node.name not in self.uids:
                self.uids[next_node.name] = self.generate_placeholder()
            for child in next_node.children:
                next_nodes.append(child)

    def iter_nodes(self):
        """
        Iterate nodes, yielding node, weight, and indentation
        """
        pass

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
            if name not in self.uids:
                return name
