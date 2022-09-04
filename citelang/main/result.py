__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import json
import os

from rich.console import Console
from rich.table import Table as RichTable

import citelang.main.colors as colors
import citelang.main.graph as graph
import citelang.utils as utils
from citelang.logger import logger

here = os.path.dirname(os.path.abspath(__file__))


class Result:
    """
    A result holds the request result and can parse or return in different formats.
    """

    def __init__(self, data, endpoint=None):
        self.endpoint = endpoint

        # Does the endpoint want to sort or otherwise order?
        data = data or {}
        if endpoint:
            self.data = self.endpoint.order(data)
        else:
            self.data = data

    def print_json(self):
        print(utils.print_json(self.data))

    def to_dict(self):
        return self.data

    def save(self, outfile):
        """
        Save to output file
        """
        logger.info("Saving to %s..." % outfile)
        utils.write_json(self.data, outfile)


class Table(Result):
    """
    A table is a result formatted as a table for the client.
    """

    def __init__(self, data, endpoint=None):
        super().__init__(data, endpoint)

        # Keep track of the max length for each field not truncated
        self.max_widths = {}
        self.ensure_complete()

    def available_width(self, columns):
        """
        Calculate available width based on fields we cannot truncate (urls)
        """
        # We will determine column width based on terminal size
        try:
            width = os.get_terminal_size().columns
        except OSError:
            width = 120

        # Calculate column width
        column_width = int(width / len(columns))
        updated = width

        for _, needed in self.max_widths.items():
            updated = updated - needed

        # We don't have enough space
        if updated < 0:
            logger.warning("Terminal is too small to correctly render!")
            return column_width

        # Otherwise, recalculate column width taking into account truncation
        # We use the updated smaller width, and break it up between columns
        # that don't have a max width
        return int(updated / (len(columns) - len(self.max_widths)))

    def ensure_complete(self):
        """
        If any data missing fields, ensure they are included
        """
        if isinstance(self.data, list):
            self.ensure_complete_list()
        # We don't check other types for now

    def ensure_complete_list(self):
        """
        Given a list result, check the fields.
        """
        fields = set()
        for entry in self.data:
            [fields.add(x) for x in entry.keys()]

        # Ensure fields are present
        truncate_list = self.endpoint.truncate_list if self.endpoint else []
        for entry in self.data:
            for field in fields:

                if field not in entry:
                    entry[field] = ""

                # We can't truncate this field!
                if field in truncate_list:

                    # We haven't seen it before
                    if field not in self.max_widths:
                        self.max_widths[field] = len(entry[field])
                    elif self.max_widths[field] < len(entry[field]):
                        self.max_widths[field] = len(entry[field])

    def table_columns(self):
        """
        Shared function to return consistent table columns
        """
        # An endpoint that returns structured json can choose to flatten
        data = self.endpoint.table_data(self.data) if self.endpoint else self.data

        # Plan to remove empty columns with count 0
        column_counts = {x: 0 for x, _ in data[0].items()}

        # Count entries for each column
        for entry in data:
            for column, value in entry.items():
                if value:
                    column_counts[column] += 1

        # Get column titles
        columns = []
        skip_list = self.endpoint.skip_list if self.endpoint else []
        contenders = list(data[0].keys())
        for column in contenders:
            if column in skip_list or column_counts[column] == 0:
                continue
            columns.append(column)
        return columns

    def table_rows(self, columns, limit=25):
        """
        Shared function to yield rows as a list
        """
        # All keys are lowercase
        column_width = self.available_width(columns)

        # An endpoint that returns structured json can choose to flatten
        data = self.endpoint.table_data(self.data) if self.endpoint else self.data
        for i, row in enumerate(data):

            # have we gone over the limit?
            if limit and i > limit:
                return

            parsed = []
            truncate_list = self.endpoint.truncate_list if self.endpoint else []
            for column in columns:
                content = str(row[column]) if row[column] else ""
                if (
                    content
                    and len(content) > column_width
                    and column not in truncate_list
                ):
                    content = content[:column_width] + "..."
                parsed.append(content)
            yield parsed

    def table(self, limit=25):
        """
        Pretty print a table of results.
        """
        table_title = ""
        if isinstance(self.data, dict) and "name" in self.data:
            table_title = " " + self.data["name"]

        endpoint_name = (
            ""
            if not self.endpoint
            else self.endpoint.name.capitalize().replace("_", " ")
        )
        table = RichTable(title="%s%s" % (endpoint_name, table_title))

        # No dependencies!
        data = self.endpoint.table_data(self.data) if self.endpoint else self.data
        if not data:
            print("This package does not have any dependencies.")
            return

        # Get column titles and unique colors
        columns = self.table_columns()
        column_colors = colors.get_rich_colors(len(columns))

        for i, column in enumerate(columns):
            title = " ".join([x.capitalize() for x in column.split("_")])
            table.add_column(title, style=column_colors[i])

        # Add rows
        for row in self.table_rows(columns, limit=limit):
            table.add_row(*row)

        # And print!
        console = Console()
        console.print(table, justify="center")


class Tree(Result):
    def __init__(self, result):
        self.result = result
        self.parse_data()

    def parse_data(self):
        """
        Parse result into data. The size is for d3, and makes each node
        relative to its siblings.
        """
        # Generate colors for all nodes
        colorset = colors.get_color_range(N=self.result.total_nodes)
        color_lookup = {
            c: str(colorset[i]) for i, c in enumerate(self.result.children_names)
        }

        data = {
            "name": self.result.name,
            "credit": self.result.credit,
            "weight": self.result.weight,
            "size": 100,
            "round_by": self.result.round_by,
            "credit_rounded": round(self.result.credit, self.result.round_by),
            "children": [],
            "color": color_lookup[self.result.name],
        }

        def add(data, children, total, levels=1):
            total += data.credit
            if data.children:
                child_size = 100 / len(data.children)
                levels += 1
            for child in data.children:
                if child.name not in color_lookup:
                    color_lookup[child.name] = colors.get_random_color()
                node = {
                    "name": child.name,
                    "credit": child.credit,
                    "credit_rounded": round(child.credit, child.round_by),
                    "weight": child.weight,
                    "size": child_size,
                    "round_by": child.round_by,
                    "children": [],
                    "color": color_lookup[child.name],
                }
                total, levels = add(child, node["children"], total, levels)
                children.append(node)
            return total, levels

        # Get total and number of levels in the tree
        total, levels = add(self.result, data["children"], 0)
        self.data = data
        self.data["total"] = total
        self.data["levels"] = levels

    def print_result(self):
        """
        Print a tree result (todo redo with color and rich)
        """

        def print_result(result, indent=2):
            print(
                "%s%20s: %s"
                % (
                    " " * indent,
                    result["name"],
                    round(result["credit"], result["round_by"]),
                )
            )
            for child in result["children"]:
                print_result(child, indent=indent * 2)

        print_result(self.data)
        print("total: %s" % round(self.data["total"], 3))


class Graph(Result):
    """
    A graph result can generate text for a graph
    """

    def __init__(self, root):
        self.root = root

    def graph(self, fmt=None):
        """
        Generate a graph of dependencies
        """
        # Select output format (default to console)
        if fmt == "dot":
            out = graph.Dot(self.root)
        elif fmt == "cypher":
            out = graph.Cypher(self.root)
        elif fmt == "gexf":
            out = graph.Gexf(self.root)
        else:
            # Only console supported for now!
            out = graph.Console(self.root)
        return out.generate()


class Treemap(Tree):
    """
    A treemap is an interactive tree.
    """

    def print_result(self):
        pass

    def save(self, outfile):
        """
        Save to output file
        """
        logger.info("Saving to %s..." % outfile)
        template = utils.read_file(os.path.join(here, "badge", "treemap.html"))
        template = template.replace("{{title}}", self.result.name)

        # Add an extra parent to the data (root) so the one child is requests
        root = {"name": "citelang", "size": 100, "children": [self.data]}
        template = template.replace("{{data}}", json.dumps(root))
        utils.write_file(template, outfile)
        logger.info("Result saved to %s" % outfile)


class Badge(Tree):
    """
    This is an static badge that uses plotly.
    """

    def print_result(self):
        pass

    def save(self, outfile):
        """
        Save to output file
        """
        import citelang.main.badge as badge

        logger.info("Saving to %s..." % outfile)

        # Force root credit value to be sum of children in first layer
        self.data["credit_label"] = self.data["credit"]
        total_credit = 0
        for child in self.data.get("children", []):
            total_credit += child["credit"]
        self.data["credit"] = total_credit

        # Add an extra parent to the data (root) so the one child is requests
        badge.generate(
            self.data,
            outfile,
            min_credit=self.result.min_credit,
            credit_split=self.result.credit_split,
        )
        logger.info("Result saved to %s" % outfile)


class InteractiveBadge(Tree):
    """
    A badge uses tree data with d3 for an interactive visualization
    """

    def print_result(self):
        pass

    def save(self, outfile):
        """
        Save to output file
        """
        logger.info("Saving to %s..." % outfile)
        template = utils.read_file(os.path.join(here, "badge", "sunburst.html"))
        template = template.replace("{{title}}", self.result.name)

        # Remove root node weight
        del self.data["weight"]

        # Add an extra parent to the data (root) so the one child is requests
        template = template.replace("{{data}}", json.dumps(self.data))
        utils.write_file(template, outfile)
        logger.info("Result saved to %s" % outfile)
