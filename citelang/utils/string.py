__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import collections.abc


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
