__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.utils as utils
import citelang.defaults as defaults

from contextlib import contextmanager
from rich.table import Table
from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live

import requests
import random
import os
import sys
import time


class Result:
    """
    A result holds the request result and can parse or return in different formats.
    """

    def __init__(self, data, endpoint):
        self.endpoint = endpoint

        # Does the endpoint want to sort or otherwise order?
        data = data or {}
        self.data = self.endpoint.order(data)

        # Keep track of the max length for each field not truncated
        self.max_widths = {}
        self.ensure_complete()

    def print_json(self):
        print(utils.print_json(self.data))

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
        for entry in self.data:
            for field in fields:

                if field not in entry:
                    entry[field] = ""

                # We can't truncate this field!
                if field in self.endpoint.truncate_list:

                    # We haven't seen it before
                    if field not in self.max_widths:
                        self.max_widths[field] = len(entry[field])
                    elif self.max_widths[field] < len(entry[field]):
                        self.max_widths[field] = len(entry[field])

    def to_dict(self):
        return self.data

    def save(self, outfile):
        """
        Save to output file
        """
        logger.info("Saving %s to %s..." % (self.title or "data", outfile))
        utils.write_json(self.data, outfile)

    @property
    def color(self):
        """
        Return a random color
        """
        return "color(" + str(random.choice(range(255))) + ")"

    def table_columns(self):
        """
        Shared function to return consistent table columns
        """
        # An endpoint that returns structured json can choose to flatten
        data = self.endpoint.table_data(self.data)

        # Get column titles
        columns = []
        contenders = list(data[0].keys())
        for column in contenders:
            if column in self.endpoint.skip_list:
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
        data = self.endpoint.table_data(self.data)

        for i, row in enumerate(data):

            # have we gone over the limit?
            if limit and i > limit:
                return

            parsed = []
            for column in columns:
                content = str(row[column]) if row[column] else ""
                if (
                    content
                    and len(content) > column_width
                    and column not in self.endpoint.truncate_list
                ):
                    content = content[:column_width] + "..."
                parsed.append(content)
            yield parsed

    def table(self, limit=25):
        """
        Pretty print a table of results.
        """
        table = Table(title=self.endpoint.title)

        # Don't reuse colors
        seen_colors = []

        # Get column titles
        columns = self.table_columns()
        for column in columns:
            color = None
            while not color or color in seen_colors:
                color = self.color
            table.add_column(column.capitalize(), style=color)

        # Add rows
        for row in self.table_rows(columns, limit=limit):
            table.add_row(*row)

        # And print!
        console = Console()
        console.print(table, justify="center")
