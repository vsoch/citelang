__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.defaults as defaults
import re

try:
    # The python manager that uses pip is more reliable
    if defaults.use_pip:
        from .pip_wrapper import PipManager as PythonManager
    else:
        from .python_base import PythonManager
except:
    # vs. static parsing, not perfect but fairly good!
    from .python_base import PythonManager

    logger.warning(
        "pip not installed on system, parsing will be done statically (less reliable)"
    )


class RequirementsManager(PythonManager):

    """
    Packages parsed from a requirements.txt file (so from pypi)
    """

    name = "requirements.txt"
    underlying_manager = "pypi"
    project_count = None
    homepage = "pypi.org/"
    color = "#006dad"
    default_language = "Python"
    default_versions = None

    def parse(self, content, **kwargs):
        """
        Parse the self.content (the requirements.txt file)
        """
        repo = self.get_repo()
        lines = content.split("\n")
        deps = self.parse_python_deps(lines)
        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo


class SetupManager(PythonManager):

    """
    Packages parsed from a requirements.txt file (so from pypi)
    """

    name = "setup.py"
    underlying_manager = "pypi"
    project_count = None
    homepage = "pypi.org/"
    color = "#006dad"
    default_language = "Python"
    default_versions = None

    def parse(self, content, **kwargs):
        """
        Parse the self.content (the requirements.txt file)
        """
        repo = self.get_repo()

        lines = []
        parsing = False
        for line in content.split("\n"):

            if "setup_requires" in line or "install_requires" in line:
                line = line.replace(" ", "")

                # It MUST be a list
                if "=[" in line:
                    parsing = True

            # We found the start and end
            if parsing and "[" in line and "]" in line:
                lines.append(line)
                parsing = False

            elif parsing and "[" in line:
                lines.append(line)

            elif parsing and "]" in line:
                lines.append(line)
                parsing = False

            elif parsing:
                lines.append(line)

        # Always skip these, try to avoid Python iterations
        skips = ["@git+", "strip()", "^#", ".git" " else ", ".format", ".startswith"]
        skip_regex = "(%s)" % "|".join(skips)

        # Clean up lines
        cleaned = []
        for line in lines:

            # Remove line immediately if starts with comment
            if line.strip().startswith("#"):
                continue

            # Get rid of comments off the bat
            line = line.split("#", 1)[0]
            terms = ["setup_requires" + x for x in [":", " :", "=", " =", ""]]
            terms += ["install_requires" + x for x in [":", " :", "=", " =", ""]]
            for term in terms + ["[", "]", '"', "'", "+", "{", "}", "(", ")"]:
                line = line.replace(term, "")

            # Get rid of any sys_platform, etc.
            line = line.split(";")[0]
            parts = line.split(",")

            # Don't add any git pip installs
            cleaned += [
                x.strip()
                for x in parts
                if x.strip() and not re.search(skip_regex, x.strip())
            ]

        # Don't include any that don't have letters
        cleaned = [
            x
            for x in cleaned
            if re.search("[a-zA-Z]", x) and not re.search("^f('|\")", x)
        ]

        # Anything that starts with a comment
        cleaned = [x.strip() for x in cleaned if not x.strip().startswith("#")]

        # Remove any variants (e.g., [all])
        cleaned = [re.sub("\[.+\]", "", x) for x in cleaned]
        deps = self.parse_python_deps(cleaned)
        repo["dependencies"] = deps
        self.data["package"] = repo
        self.data["dependencies"] = deps
        return repo
