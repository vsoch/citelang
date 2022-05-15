__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Custom package managers not in libraries IO

from .github import GitHubManager
from .spack import SpackManager
from .pypi_requirements import RequirementsManager, SetupManager
from .cran_description import RPackageManager
from .ruby_gem import GemfileManager
from .go_mod import GoModuleManager
from .npm_packages import NPMPackageManager
from .cpp_cmakelist import CMakeListManager

# Registered endpoints (populated on init)
managers = {}
manager_names = []
filesystem_manager_names = []

for manager in [
    GitHubManager,
    SpackManager,
    RequirementsManager,
    RPackageManager,
    SetupManager,
    GemfileManager,
    GoModuleManager,
    NPMPackageManager,
    CMakeListManager,
]:
    manager_names.append(manager.name)
    managers[manager.name] = manager

    if manager.filesystem_manager:
        filesystem_manager_names.append(manager.name)

manager_names.sort()
filesystem_manager_names.sort()
