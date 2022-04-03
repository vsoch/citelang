__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Custom package managers not in libraries IO

from .github import GitHubManager
from .spack import SpackManager
from .pypi_requirements import RequirementsManager
from .cran_description import RPackageManager

# Registered endpoints (populated on init)
managers = {}
manager_names = []

for manager in [GitHubManager, SpackManager, RequirementsManager, RPackageManager]:
    manager_names.append(manager.name)
    managers[manager.name] = manager

manager_names.sort()
