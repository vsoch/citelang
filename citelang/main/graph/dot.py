__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger

import random
import sys

from .base import GraphBase


class Dot(GraphBase):
    """
    The dot format is for graphviz
    """

    def generate(self, graphname=None, fontname="Arial"):
        if self.outfile != sys.stdout:
            logger.info("Output will be written to %s" % self.outfile)
            fd = open(self.outfile, "w")
        else:
            fd = self.outfile

        graphname = graphname or self.data.name
        fd.write("digraph " + graphname + " {\n ratio=0.562;\n")

        # Do we want to render using a certain font?
        for node in ["graph", "node", "edge"]:
            fd.write(" " + node + ' [fontname="' + fontname + '"];\n')

        # Color for root (first) and then linked libs, and symbols
        colors = [
            "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
            for i in range(2)
        ]

        root_color = colors.pop()
        node_color = colors.pop()

        # Create graph with nodes
        next_nodes = [self.data]
        first_node = True
        while next_nodes:
            next_node = next_nodes.pop(0)
            label = self.uids[next_node.name]
            name = "%s (%s)" % (next_node.name, round(next_node.credit, 3))
            if first_node:
                fd.write(
                    ' %s [label="%s" tooltip="%s", style=filled, color="%s"];\n'
                    % (label, name, name, root_color)
                )
                first_node = False
            else:
                fd.write(
                    ' %s [label="%s" tooltip="%s", style=filled, color="%s"];\n'
                    % (label, name, name, node_color)
                )
            for child in next_node.children:
                next_nodes.append(child)

        # Now create links
        next_nodes = [self.data]
        while next_nodes:
            next_node = next_nodes.pop(0)
            label = self.uids[next_node.name]
            name = "%s (%s)" % (next_node.name, round(next_node.credit, 3))
            for child in next_node.children:
                label_to = self.uids[child.name]
                fd.write(
                    ' %s -> %s [label=" depends on " tooltip="%s -> %s"];\n'
                    % (label, label_to, next_node.name, child.name)
                )
                next_nodes.append(child)

        fd.write("\n}\n")
        if self.outfile != sys.stdout:
            fd.close()
