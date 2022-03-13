__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import citelang.utils as utils

apiroot = "https://libraries.io"

install_dir = utils.get_installdir()

# User home
user_home = os.path.expanduser("~/")

# CiteLang default home
citelang_home = os.path.join(user_home, ".citelang")

# Replacements allowed
reps = {
    "$install_dir": install_dir,
    "$root_dir": os.path.dirname(install_dir),
    "$user_home": user_home,
    "$citelang_home": citelang_home,
}

# The default settings file in the install root
default_settings_file = os.path.join(reps["$install_dir"], "settings.yml")

# The user settings file can be created to over-ride default
user_settings_file = os.path.join(citelang_home, "settings.yml")

# variables in settings that allow environment variable expansion
allowed_envars = ["cache_dir"]
