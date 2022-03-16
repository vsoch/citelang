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


versionProperties = {
    "number": {"type": ["string", "number"]},
    "published_at": {"type": ["null", "string"]},
    "spdx_expression": {"type": ["null", "string"]},
    "original_license": {"type": ["null", "string"]},
    "researched_at": {"type": ["null", "string"]},
    "repository_sources": {"type": "array", "items": {"type": "string"}},
}

versions = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["number"],
        "properties": versionProperties,
    },
}


# This matches a libraries.io package
packageProperties = {
    "dependent_repos_count": {"type": "number"},
    "dependents_count": {"type": "number"},
    "deprecation_reason": {"type": ["null", "string"]},
    "description": {"type": ["null", "string"]},
    "forks": {"type": "number"},
    "homepage": {"type": ["null", "string"]},
    "keywords": {"type": "array", "items": {"type": "string"}},
    "language": {"type": ["null", "string"]},
    "latest_download_url": {"type": ["null", "string"]},
    "latest_release_number": {"type": ["null", "string"]},
    "latest_release_published_at": {"type": ["null", "string"]},
    "latest_stable_release_number": {"type": ["null", "string"]},
    "latest_stable_release_published_at": {"type": ["null", "string"]},
    "license_normalized": {"type": "boolean"},
    "licenses": {"type": ["null", "string"]},
    "name": {"type": "string"},
    "normalized_licenses": {"type": "array", "items": {"type": "string"}},
    "package_manager_url": {"type": ["null", "string"]},
    "platform": {"type": ["null", "string"]},
    "rank": {"type": ["null", "number"]},
    "repository_license": {"type": ["null", "string"]},
    "repository_url": {"type": ["null", "string"]},
    "stars": {"type": ["null", "number"]},
    "status": {"type": ["null", "string"]},
    "versions": versions,
}

# We use libraries.io schemas to ensure consistency,
# and we only require what we absolutely need!
package = {
    "$schema": schema_url,
    "title": "Package Schema",
    "type": "object",
    "required": ["description", "homepage", "language", "name", "versions"],
    "properties": packageProperties,
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
