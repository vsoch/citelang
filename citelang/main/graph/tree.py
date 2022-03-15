__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from rich import print
from rich.text import Text
from rich.tree import Tree
import random

# Randomly select an AMAZING icon
# Note some of these require TWO spaces after the icon to render properly!
icons = ["⭐️ ", "✨️ ", "💛️ ", "🔷️ ", "❤️  ", "💜️ ", "🧡️ ", "💗️ ", "🔴️ ", "♦️  ", "🔶️ "]


def print_tree(root):
    node = Text(f"🦄️ {root.name}", "bold magenta")
    credit = round(root.credit, 3)
    node.append(f" ({credit})", "blue")
    tree = Tree(
        node,
        guide_style="bold bright_blue",
    )

    # Randomly select icons
    icon = random.choice(icons)
    generate_tree(root, tree=tree, icon=icon)
    print(tree)


def generate_tree(next_node, icon, tree=None) -> None:
    """
    Recursively build a Tree with a dependency result
    """
    for child in next_node.children:
        # We won't have a tree on the first run
        credit = round(child.credit, 3)
        node = Text(child.name, "green")
        node.highlight_regex(r"\..*$", "bold red")
        node.stylize(f"link file://{child.name}")
        node.append(f" ({credit})", "blue")
        branch = tree.add(Text(icon) + node)
        generate_tree(child, tree=branch, icon=icon)
