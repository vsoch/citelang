__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


from .base import GraphBase
from .tree import print_tree


class Console(GraphBase):
    def generate(self):
        print_tree(self.data)
