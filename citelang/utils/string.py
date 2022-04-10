__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import collections.abc
import os


def get_terminal_pad(size):
    """
    Given an input of a particular size, get an estimated terminal left padding
    """
    try:
        # This will fail in a test environment
        return max(os.get_terminal_size().columns - size, 0)
    except:
        return 30


def update_nested(data, update):
    """
    recursive function to update nested dict
    """
    for k, v in update.items():
        if isinstance(v, collections.abc.Mapping):
            data[k] = update_nested(data.get(k, {}), v)
        elif k not in data:
            data[k] = v
        elif (
            k in data
            and isinstance(data[k], (int, float))
            and isinstance(update[k], (int, float))
        ):
            data[k] = data[k] + data[v]
    return data
