__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


from citelang.logger import logger

import sys

from .base import GraphBase


class Cypher(GraphBase):
    def generate(self):
        if self.outfile == sys.stdout:
            fd = sys.stdout
        else:
            logger.info("Output will be written to %s" % self.outfile)
            fd = open(self.outfile, "w")

        fd.write("CREATE ")

        # Create graph with nodes
        next_nodes = [self.data]
        while next_nodes:
            next_node = next_nodes.pop(0)
            label = self.uids[next_node.name]
            name = "%s (%s)" % (next_node.name, round(next_node.credit, 3))
            fd.write("(%s:PACKAGE {name: '%s', label: '%s'}),\n" % (label, name, label))
            for child in next_node.children:
                next_nodes.append(child)

        # Now create links
        next_nodes = [self.data]
        text = ""
        while next_nodes:
            next_node = next_nodes.pop(0)
            label = self.uids[next_node.name]
            name = "%s (%s)" % (next_node.name, round(next_node.credit, 3))
            for i, child in enumerate(next_node.children):
                label_to = self.uids[child.name]
                text += "(%s)-[:DEPENDSON]->(%s),\n" % (label, label_to)
                next_nodes.append(child)

        text = text.strip(",\n")
        fd.write(text + ";\n")
        if self.outfile != sys.stdout:
            fd.close()
