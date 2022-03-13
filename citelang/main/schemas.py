__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


schema_url = "http://json-schema.org/draft-07/schema"


# The simplest form of aliases is key/value pairs
keyvals = {
    "type": "object",
    "patternProperties": {
        "\\w[\\w-]*": {"type": "string"},
    },
}


# Currently all of these are required
settingsProperties = {
    "cache_dir": {"type": "string"},
    "disable_cache": {"type": "boolean"},
    "disable_memory_cache": {"type": "boolean"},
}

settings = {
    "$schema": schema_url,
    "title": "Settings Schema",
    "type": "object",
    "required": [
        "disable_memory_cache",
        "disable_cache",
        "cache_dir",
    ],
    "properties": settingsProperties,
    "additionalProperties": False,
}
