__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

__version__ = "0.0.12"
AUTHOR = "Vanessa Sochat"
EMAIL = "vsoch@users.noreply.github.com"
NAME = "citelang"
PACKAGE_URL = "https://github.com/vsoch/citelang"
KEYWORDS = "credit, software, rseng, research software"
DESCRIPTION = "Credit parser and markdown language for scientific software."
LICENSE = "LICENSE"

################################################################################
# Global requirements

# Since we assume wanting Singularity and lmod, we require spython and Jinja2

INSTALL_REQUIRES = (
    ("rich", {"min_version": None}),
    ("pyaml", {"min_version": None}),
    ("jsonschema", {"min_version": None}),
    ("requests", {"min_version": None}),
    ("colour", {"min_version": None}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

################################################################################
# Submodule Requirements (versions that include database)

INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES
