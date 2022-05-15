__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.main.cache as cache
import citelang.main.endpoints as endpoints
import citelang.main.result as results
import citelang.main.graph as graph
import citelang.main.package as package
import citelang.main.packages as packages


class BaseClient:
    """
    A baseclient controls interactions with endpoints and the cache.
    """

    def __init__(self, quiet=False, **kwargs):
        self.quiet = quiet
        self.cache = cache.cache

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[citelang-client]"

    def dependencies(self, manager, name, use_cache=True):
        """
        Get dependencies for a package. If no version, use latest.
        """
        self.check_manager(manager, use_cache)
        pkg = package.Package(manager, name, use_cache=use_cache)
        return pkg.dependencies()

    def package_managers(self, use_cache=True):
        """
        Get a listing of package managers supported on libraries.io
        """
        result = self.cache.get("package_managers")
        if not result or not use_cache:
            logger.info("Retrieving new result for package managers...")
            result = endpoints.get_endpoint("package_managers")

            # Update custom package managers
            names = [x["name"] for x in result.data]
            result.data += [
                p().info()
                for _, p in packages.managers.items()
                if p().info()["name"] not in names
            ]
        else:
            result = endpoints.get_endpoint("package_managers", data=result)

        # If cache is enabled, we save the result
        self.cache.set("package_managers", result)
        return result

    def check_manager(self, name, use_cache=True):
        """
        Check if a package manager is supported
        """
        if name in packages.manager_names:
            return
        managers = self.package_managers(use_cache)

        # Ensure the manager is allowed
        if managers.data:
            managers = [x["name"].lower() for x in managers.data]
            if name not in managers and name is not None:
                managers = "\n".join(managers)
                logger.exit(f"{name} is not a known manager. Choices are:\n{managers}")

    def graph(self, fmt=None, *args, **kwargs):
        """
        Generate a graph for a package.

        credit_split is how to split credit between some package and its dependents. E.g., 0.5 means 50/50. 0.8 means
        the main package gets 80%, and dependencies split 20%. We go up until the min credit 0.05 at which case we
        stop adding.
        """
        root = self._graph(*args, **kwargs)
        return results.Graph(root).graph(fmt=fmt)

    def badge(self, template="static", *args, **kwargs):
        """
        Generate a badge for a package
        """
        root = self._graph(*args, **kwargs)
        if template == "treemap":
            return results.Treemap(root)
        elif template == "sunburst":
            return results.InteractiveBadge(root)
        return results.Badge(root)

    def _graph(
        self,
        manager,
        name,
        use_cache=True,
        max_depth=None,
        max_deps=None,
        min_credit=0.01,
        credit_split=0.01,
        pkg=None,
    ):
        """
        Shared 'private' function to generate graph
        """
        self.check_manager(manager, use_cache)

        # Allow the caller to provide a pre-generated (often custom) package
        if not pkg:
            pkg = package.get_package(manager, name, use_cache=use_cache)

        # E.g., a requirements.txt file underlying manager is pypi
        if pkg.underlying_manager:
            manager = pkg.underlying_manager.underlying_manager

        # keep track of deps (we only care about name, not version) and names
        seen = set()
        node_names = set()

        # Top node gets full credit 1.0 (to split between itself and deps)
        root = graph.Node(
            obj=pkg,
            weight=1.0,
            credit_split=credit_split,
            depth=0,
            min_credit=min_credit,
            is_root=True,
        )

        # A pointer to the next node
        next_nodes = [root]

        # Booleans to trigger exiting parser
        stop_looking = False

        # Keep handle to previous children in case we stop looking
        previous = []

        while next_nodes and not stop_looking:
            next_node = next_nodes.pop(0)

            # Sometimes we know a package name / version but cannot get deps
            try:
                deps = next_node.obj.dependencies(return_data=True)
            except:
                deps = []
            [
                node_names.add(d["name"])
                for d in deps
                if "name" in d and not d["name"].startswith("__")
            ]

            # Stopping point - exceeded max depth
            if max_depth and next_node.depth > max_depth:
                stop_looking = True

            # Stopping point - exceeded max deps (plus 1 for original package)
            if max_deps and len(seen) + 1 > max_deps:
                stop_looking = True

            seen.add(next_node.name)
            node_names.add(next_node.name)

            if not deps:
                continue

            # How much credit for each of the new deps?
            # credit for all deps AS a percentage of the weight BROKEN into number of deps
            dep_credit = ((1 - credit_split) * next_node.weight) / len(deps)

            # Stopping point - dependency credit is too small
            if dep_credit < min_credit:
                stop_looking = True

            # If we are stopping, time to break and distribute remaining credit
            # to nodes we couldn't parse children for.
            if stop_looking:

                # We haven't parsed this one yet
                next_node.total_credit = next_node.weight

                # Give all remaining credit to the node we aren't parsing
                for node in previous:

                    # We might have added and given credit to some children
                    if node.children:

                        # Redistribute credit amongst children that were > threshold
                        dep_credit = ((1 - credit_split) * node.weight) / len(
                            node.children
                        )
                        for child in node.children:
                            child.total_credit = dep_credit

                        # The node's credit is that weight minus total dep credit
                        node.total_credit = node.weight - (
                            dep_credit * len(node.children)
                        )
                    else:
                        node.total_credit = node.weight
                break

            # Calculate credit for each dependency and add as child
            for dep in deps:

                # Haven't seen this case, but just a check
                dep_name = dep["name"] or dep["project_name"]
                if not dep_name or dep_name.startswith("__"):
                    continue

                depnode = package.get_package(manager, dep_name, use_cache=use_cache)
                child = graph.Node(
                    obj=depnode,
                    weight=dep_credit,
                    credit_split=credit_split,
                    depth=next_node.depth + 1,
                    min_credit=min_credit,
                )
                next_node.add_child(child)
                next_nodes.append(child)

                # Store previous if we need to update weight
                previous.append(child)

        # Add total node count to root
        root.children_names = list(node_names)
        return root

    def credit(self, *args, **kwargs):
        """
        Get the credit root node, then do additional graph parsing.
        """
        root = self._graph(*args, **kwargs)
        return results.Tree(root)

    def package(self, manager, name, use_cache=True):
        """
        Lookup a package in a specific package manager
        """
        self.check_manager(manager, use_cache)
        pkg = package.get_package(manager, name, use_cache=use_cache)
        return pkg.info()
