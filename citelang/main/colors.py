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


def get_rich_color():
    """
    Return a random color
    """
    return "color(" + str(random.choice(range(255))) + ")"


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
    palette = get_random_palette()
    start_color = colour.Color("#" + palette.pop(random.choice(range(len(palette)))))
    end_color = colour.Color("#" + palette.pop(random.choice(range(len(palette)))))
    return list(start_color.range_to(end_color, N))
