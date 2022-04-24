__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import colour
import random

# Palettes

# https://coolors.co/a80874-ac4697-b083b9-b4c0dc-b7fdfe-8bf8c5-5ef38c-45c556-2b9720-343a1a
palettes = {
    "radish": [
        "a80874",
        "ac4697",
        "b083b9",
        "b4c0dc",
        "b7fdfe",
        "8bf8c5",
        "5ef38c",
        "45c556",
        "2b9720",
        "343a1a",
    ]
}


# Generally safe colors for light or black backgrounds in the 16 color palette.
# See also https://robotmoon.com/256-colors/
termColors = [
    1,
    2,
    3,
    4,
    5,
    6,
    9,
    10,
    11,
    12,
    13,
    14,
]


def get_random_color():
    return "#" + "".join([random.choice("ABCDEF0123456789") for i in range(6)])


def get_rich_color():
    """
    Return a random color
    """
    return "color(" + str(random.choice(termColors)) + ")"


def get_rich_colors(N):
    """
    Randomly generate N colors for rich (integers)
    """
    chosen_colors = []

    for i in range(N):
        color = None
        while not color or color in chosen_colors:
            color = get_rich_color()
        chosen_colors.append(color)
    return chosen_colors


def get_random_palette():
    """
    Choose a random color palette
    """
    name = random.choice(list(palettes.keys()))
    return palettes[name]


def get_color_range(N=100):
    """
    Get a color range, size N
    """
    start_color = colour.Color(get_random_color())
    end_color = colour.Color(get_random_color())
    return list(start_color.range_to(end_color, N))
