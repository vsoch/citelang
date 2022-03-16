__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


from citelang.logger import logger
import sys

from datetime import datetime
from .base import GraphBase

template = """<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft" version="1.1" xmlns:viz="http://www.gexf.net/1.1draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.1draft http://www.gexf.net/1.1draft/gexf.xsd">
    <meta lastmodifieddate="%s">
        <creator>citelang</creator>
        <description>Citation credit analysis of %s</description>
    </meta>
    <graph defaultedgetype="directed" idtype="string" type="static">
    <nodes>
"""


class Gexf(GraphBase):
    def generate(self):
        if self.outfile != sys.stdout:
            logger.info("Output will be written to %s" % self.outfile)
            fd = open(self.outfile, "w")
        else:
            fd = self.outfile

        today = datetime.now().strftime("%Y-%m-%d")

        # Add the binary name and date to the template
        fd.write(template % (today, self.data.name))

        # Create graph with nodes
        next_nodes = [self.data]
        while next_nodes:
            next_node = next_nodes.pop(0)
            label = self.uids[next_node.name]
            name = "%s (%s)" % (next_node.name, round(next_node.credit, 3))
            fd.write('        <node id="%s" label="%s"/>\n' % (label, name))
            for child in next_node.children:
                next_nodes.append(child)

        fd.write("    </nodes>\n    <edges>")

        # Now create links
        next_nodes = [self.data]
        while next_nodes:
            next_node = next_nodes.pop(0)
            label = self.uids[next_node.name]
            name = "%s (%s)" % (next_node.name, round(next_node.credit, 3))
            for child in next_node.children:
                label_to = self.uids[child.name]
                fd.write(
                    '        <edge id="%s" source="%s" target="%s" label="depends on"/>\n'
                    % (label_to, label, label_to)
                )
                next_nodes.append(child)

        fd.write("    </edges>\n")
        fd.write("</graph>\n")
        fd.write("</gexf>\n")

        if self.outfile != sys.stdout:
            fd.close()
