__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
import re
import shutil

import jsonschema
import yaml

import citelang.defaults as defaults
import citelang.main.schemas as schemas
import citelang.utils
from citelang.logger import logger


class SettingsBase:
    def __init__(self, settings_file=None, validate=True):
        """
        Create a new settings object, which requires a settings file to load
        """
        self.settings_file = None
        self.user_settings = None
        self.load(settings_file)
        if validate:
            self.validate()

    def __str__(self):
        return "[citelang-settings]"

    def __repr__(self):
        return self.__str__()

    def validate(self):
        """
        Validate the loaded settings with jsonschema
        """
        jsonschema.validate(instance=self._settings, schema=schemas.settings)

    def inituser(self):
        """
        Create a user specific config in user's home.
        """
        user_home = os.path.dirname(defaults.user_settings_file)
        if not os.path.exists(user_home):
            os.makedirs(user_home)
        if os.path.exists(defaults.user_settings_file):
            logger.exit(
                "%s already exists! Remove first before re-creating."
                % defaults.user_settings_file
            )
        shutil.copyfile(self.settings_file, defaults.user_settings_file)
        logger.info("Created user settings file %s" % defaults.user_settings_file)

    def edit(self):
        """
        Interactively edit a config file.
        """
        if not self.settings_file or not os.path.exists(self.settings_file):
            logger.exit("Settings file not found.")

        # Make sure editor exists first!
        editor = citelang.utils.which(self.config_editor)
        if editor["return_code"] != 0:
            logger.exit(
                "Editor '%s' not found! Update with citelang config set config_editor:<name>"
                % self.config_editor
            )
        citelang.utils.run_command(
            [self.config_editor, self.settings_file], stream=True
        )

    def get_settings_file(self, settings_file=None):
        """
        Get the preferred user settings file, set user settings if exists.
        """
        # Always use environment first
        env_settings = None
        if defaults.env_settings_file and os.path.exists(defaults.env_settings_file):
            env_settings = defaults.env_settings_file

        # Only consider user settings if the file exists!
        user_settings = None
        if os.path.exists(defaults.user_settings_file):
            user_settings = defaults.user_settings_file

        # First preference to env_settings, then user settings, then default
        return env_settings or user_settings or defaults.default_settings_file

    def load(self, settings_file=None):
        """
        Load the settings file into the settings object
        """
        # Get the preferred settings flie
        self.settings_file = self.get_settings_file(settings_file)

        # Exit quickly if the settings file does not exist
        if not os.path.exists(self.settings_file):
            logger.exit("%s does not exist." % self.settings_file)

        # Always load default settings first
        with open(defaults.default_settings_file, "r") as fd:
            self._settings = yaml.load(fd.read(), Loader=yaml.SafeLoader)

        # Update with user or custom settings if not equal to default
        if self.settings_file != defaults.default_settings_file:
            with open(self.settings_file, "r") as fd:
                self._settings.update(yaml.load(fd.read(), Loader=yaml.SafeLoader))

    def get(self, key, default=None):
        """
        Get a settings value, doing appropriate substitution and expansion.
        """
        # This is a reference to a dictionary (object) setting
        if ":" in key:
            key, subkey = key.split(":")
            value = self._settings[key][subkey]
        else:
            value = self._settings.get(key, default)
        value = self._substitutions(value)
        # If we allow environment substitution, do it
        if key in defaults.allowed_envars and value:
            if isinstance(value, list):
                value = [os.path.expandvars(v) for v in value]
            else:
                value = os.path.expandvars(value)
        return value

    def __getattr__(self, key):
        """
        A direct get of an attribute, but default to None if doesn't exist
        """
        return self.get(key)

    def add(self, key, value):
        """
        Add a value to a list parameter
        """
        value = self.parse_boolean(value)

        # We can only add to lists
        current = self._settings.get(key)
        if current and not isinstance(current, list):
            logger.exit("You cannot only add to a list variable.")
        value = self.parse_null(value)

        if value not in current:
            # Add to the beginning of the list
            current = [value] + current
            self._settings[key] = []
            [self._settings[key].append(x) for x in current]
            self.change_validate(key, value)
            logger.warning(
                "Warning: Check with citelang config edit - ordering of list can change."
            )

    def remove(self, key, value):
        """
        Remove a value from a list parameter
        """
        current = self._settings.get(key)
        if current and not isinstance(current, list):
            logger.exit("You cannot only remove from a list variable.")
        if not current or value not in current:
            logger.exit("%s is not in %s" % (value, key))
        current.pop(current.index(value))
        self._settings[key] = current
        self.change_validate(key, current)
        logger.warning(
            "Warning: Check with citelang config edit - ordering of list can change."
        )

    def parse_boolean(self, value):
        """
        If the value is True/False, ensure we return a boolean
        """
        if isinstance(value, str) and value.lower() == "true":
            value = True
        elif isinstance(value, str) and value.lower() == "false":
            value = False
        return value

    def parse_null(self, value):
        """
        Given a null or none from the command line, ensure parsed as None type
        """
        if isinstance(value, str) and value.lower() in ["none", "null"]:
            return None

        # Ensure we strip strings
        if isinstance(value, str):
            value = value.strip()
        return value

    def set(self, key, value):
        """
        Set a setting based on key and value. If the key has :, it's nested
        """
        value = self.parse_boolean(value)

        # List values not allowed for set
        current = self._settings.get(key)
        if current and isinstance(current, list):
            logger.exit("You cannot use 'set' for a list. Use add/remove instead.")

        # This is a reference to a dictionary (object) setting
        if isinstance(value, str) and ":" in value:
            subkey, value = value.split(":")
            value = self.parse_boolean(value)
            value = self.parse_null(value)
            self._settings[key][subkey] = value
        else:
            value = self.parse_null(value)
            self._settings[key] = value

        # Validate and catch error message cleanly
        self.change_validate(key, value)

    def change_validate(self, key, value):
        """
        A courtesy function to validate a new config addition.
        """
        # Don't allow the user to add a setting not known
        try:
            self.validate()
        except jsonschema.exceptions.ValidationError as error:
            logger.exit(
                "%s:%s cannot be added to config: %s" % (key, value, error.message)
            )

    def _substitutions(self, value):
        """
        Given a value, make substitutions
        """
        if isinstance(value, bool) or not value:
            return value

        # Currently dicts only support boolean or null so we return as is
        elif isinstance(value, dict):
            return value

        for rep, repvalue in defaults.reps.items():
            if isinstance(value, list):
                value = [x.replace(rep, repvalue) for x in value]
            else:
                value = value.replace(rep, repvalue)

        return value

    def delete(self, key):
        if key in self._settings:
            del self._settings[key]

    def save(self, filename=None):
        """
        Save settings, but do not change order of anything.
        """
        filename = filename or self.settings_file
        if not filename:
            logger.exit("A filename is required to save to.")

        with open(filename, "w") as fd:
            yaml.dump(self._settings, fd)

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key, value

    def update_params(self, params):
        """
        Update a configuration on the fly (no save) only for set/add/remove.
        Unlike the traditional set/get/add functions, this function expects
        each entry in the params list to start with the action, e.g.:

        set:name:value
        add:name:value
        rm:name:value
        """
        # Cut out early if params not provided
        if not params:
            return

        for param in params:
            if not re.search("^(add|set|rm)", param, re.IGNORECASE) or ":" not in param:
                logger.warning(
                    "Parameter update request must start with (add|set|rm):, skipping %s"
                )
            command, param = param.split(":", 1)
            self.update_param(command.lower(), param)

    def update_param(self, command, param):
        """
        Given a parameter, update the configuration on the fly if it's in set/add/remove
        """
        if ":" not in param:
            logger.warning(
                "Param %s is missing a :, should be key:value pair. Skipping." % param
            )
            return

        key, value = param.split(":", 1)
        if command == "set":
            self.set(key, value)
            logger.info("Updated %s to be %s" % (key, value))
        elif command == "add":
            self.add(key, value)
            logger.info("Added %s to %s" % (key, value))
        elif command == "remove":
            self.remove(key, value)
            logger.info("Removed %s from %s" % (key, value))


class Settings(SettingsBase):
    """
    The settings class is a wrapper for easily parsing a settings.yml file.

    We parse into a query-able class. It also gives us control to update settings,
    meaning we change the values and then write them to file. It's basically
    a dictionary-like class with extra functions.
    """

    def __init__(self, settings_file, validate=True):
        """
        Create a new settings object, which requires a settings file to load
        """
        self.load(settings_file)
        if validate:
            self.validate()


# Global settings
def init_settings(validate=True):
    return SettingsBase(validate=validate)


cfg = init_settings()
