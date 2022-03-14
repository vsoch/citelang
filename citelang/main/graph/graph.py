__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import citelang.utils as utils
from citelang.logger import logger
import sys


class Node:
    def __init__(self, obj, weight, credit_split=0.5, depth=0):
        """
        A graph node has a name (or object), weight, and children
        """
        self.obj = obj
        self.weight = weight
        self.children = []
        self.credit_split = credit_split
        self.depth = depth

        # If we stop parsing we can set this credit to whatever the node and
        # children would originall get
        self.total_credit = None

    @property
    def name(self):
        return self.obj.name

    def add_child(self, child):
        """
        Add child ensures we increment the depth by 1
        """
        child.depth = self.depth + 1
        self.children.append(child)

    @property
    def credit(self):
        if self.total_credit:
            return self.total_credit
        return self.credit_split * self.weight


class Graph:
    def __init__(self, root):
        self.root = root
