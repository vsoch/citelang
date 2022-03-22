__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


class Node:
    def __init__(
        self, obj, weight, credit_split=0.5, depth=0, min_credit=0.01, is_root=False
    ):
        """
        A graph node has a name (or object), weight, and children
        """
        self.obj = obj
        self.weight = weight
        self.children = []
        self.credit_split = credit_split
        self.depth = depth
        self.min_credit = min_credit
        self.is_root = is_root

        # If we stop parsing we can set this credit to whatever the node and
        # children would originall get
        self.total_credit = None
        self.children_names = []

    def iternodes(self):
        """
        Iterate through all nodes of the graph
        """
        nodes = [self]
        while nodes:
            node = nodes.pop(0)
            yield node
            nodes += node.children

    @property
    def total_nodes(self):
        return len(self.children_names)

    @property
    def name(self):
        return self.obj.name

    @property
    def round_by(self):
        value = str(self.min_credit).split(".", 1)[-1]
        if not value:
            return 3
        return len(value)

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
