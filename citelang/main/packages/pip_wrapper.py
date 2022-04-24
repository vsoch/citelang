__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from pip._internal.commands.install import (
    InstallCommand,
    reject_location_related_install_options,
)
from pip._internal.cli.cmdoptions import make_target_python
from pip._internal.cli.main_parser import create_main_parser
from pip._internal.req.req_tracker import get_requirement_tracker
from pip._internal.utils.temp_dir import TempDirectory
from pip._internal.cli import cmdoptions
from pip._internal.cache import WheelCache

from citelang.logger import logger
import citelang.utils as utils
import re
import os

from .base import PackagesFromFile


class PackageLister(InstallCommand):
    """
    A wrapper to the pypi install command that simply resolves dependencies
    and saves the listing. A requirements.txt file will work outside of context,
    however a setup.py typically needs external dependencies (and if it does
    not work, will fall back to the static parser).
    """

    def run(self, options, args):
        cmdoptions.check_dist_restriction(options, check_target=True)
        options.use_user_site = True
        session = self.get_default_session(options)
        target_python = make_target_python(options)
        finder = self._build_package_finder(
            options=options,
            session=session,
            target_python=target_python,
            ignore_requires_python=options.ignore_requires_python,
        )
        try:
            reqs = self.get_requirements(args, options, finder, session)
            self._citelang_success = True

            # requirements.txt will be parsed already
            if "." not in args:
                self._citelang_reqs = reqs
                return 0

            # If we are installing a setup.py, we need to parse
            for req in reqs:
                req.permit_editable_wheels = True

            req_tracker = self.enter_context(get_requirement_tracker())
            wheel_cache = WheelCache(options.cache_dir, options.format_control)
            reject_location_related_install_options(reqs, options.install_options)
            directory = TempDirectory(
                delete=True,
                kind="install",
                globally_managed=True,
            )
            preparer = self.make_requirement_preparer(
                temp_build_dir=directory,
                options=options,
                req_tracker=req_tracker,
                session=session,
                finder=finder,
                use_user_site=options.use_user_site,
                verbosity=self.verbosity,
            )
            resolver = self.make_resolver(
                preparer=preparer,
                finder=finder,
                options=options,
                wheel_cache=wheel_cache,
                use_user_site=options.use_user_site,
                ignore_installed=options.ignore_installed,
                ignore_requires_python=options.ignore_requires_python,
                force_reinstall=options.force_reinstall,
                upgrade_strategy="to-satisfy-only",
                use_pep517=options.use_pep517,
            )
            self.trace_basic_info(finder)
            self._citelang_reqs = resolver.resolve(
                reqs, check_supported_wheels=False
            ).all_requirements

        except Exception as err:
            self._citelang_success = False
            logger.warning(
                "Issue using pip to resolve dependencies: %s, will fall back to static parser."
                % err
            )
            self._citelang_reqs = []

        # Always return success to main
        return 0


class PipManager(PackagesFromFile):
    def parse_python_deps(self, lines):
        """
        Shared function for deriving a list of python dependencies from lines
        """
        parser = create_main_parser()
        args = []
        if self.filename.endswith("requirements.txt"):
            # Generate args based on a faux command
            args = ["install", "-r", "requirements.txt"]
        if self.filename.endswith("setup.py"):
            args = ["install", "."]

        general_options, args_else = parser.parse_args(args)
        cmd_name = args_else[0]
        cmd_args = args[:]
        cmd_args.remove(cmd_name)

        # Instead of parsing the content we instead parse the filename
        dirname = os.path.dirname(self.filename)
        lister = PackageLister("citelang", "listing of Citelang packages")

        with utils.workdir(dirname):
            lister.main(cmd_args)

        # If we don't have deps, fall back to static parser
        if not lister._citelang_success:
            from .python_base import PythonManager as FallbackParser

            FallbackParser.name = self.name
            mgr = FallbackParser(package_name=self.package_name, filename=self.filename)
            return mgr.parse_python_deps(lines=lines, filename=self.filename)

        deps = []
        for dep in lister._citelang_reqs:
            package_name = dep.name
            version = None

            # We can only use package names that could be on pip
            if not package_name:
                continue
            if dep.specifier:
                version = str(dep.specifier)
            if version and re.search("(==|~=|<=|>=|<|>|!=)", version):
                version = re.sub("(==|~=|<=|>=|<|>|!=)", "", version).strip()

            # First add requirements (names and pypi manager) to deps
            pkg = self.get_package(package_name, version)
            if not pkg:
                pkg = self.get_package(package_name)
                if not pkg:
                    logger.warning("Issue getting package %s, skipping" % package_name)
                    continue

            # Ensure we have version, fallback to latest
            if not version:
                version = pkg.data["latest_release_number"]

            # Require saving to cache here - many expensive calls
            cache_name = f"package/pypi/{package_name}/{version}"
            self.cache.set(cache_name, pkg)

            # use latest release version. This will be wrong for an old
            # dependency, but it's not worth it to make a ton of extra API calls
            dep = {
                "name": package_name,
                "project_name": package_name,
                "number": version,
                "published_at": pkg.data["latest_stable_release_published_at"],
                "researched_at": None,
                "spdx_expression": "NOASSERTION",
                "original_license": pkg.data["licenses"],
                "repository_sources": ["Pypi"],
            }
            deps.append(dep)
        return deps
