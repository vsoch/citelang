__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger, spinner
import citelang.utils as utils

import re
import os
import multiprocessing

# global pool used by parser functions
pool = None


# Patterns to parse git blame
patterns = {
    "commit": "^([0-9a-f]{40})",
    "author": "^author (.*)$",
    "text": "^\t(.*)$",
    "time": "^committer-time (.*)$",
}


def blame_task(args):
    """
    Run the blame task. This is based on logic from pypi contrib.
    If there is an empty result, meaning no commits match or there is an issue
    with blame, record the file as empty in the cache so we don't try again.
    """
    # Sploot out args into variables
    root, commit, path, save_to, shallow = args

    # If we have the history already, return
    if os.path.exists(save_to):
        return {
            "output": utils.read_json(save_to),
            "path": path,
            "exist": True,
            "empty": "",
        }

    # Atomic save
    tmp_file = save_to + ".tmp.%d" % os.getpid()

    # Asssemble command
    command = ["git", "blame", "-w", "--line-porcelain"]

    # find line copies and movements across files (more shallow result)
    if shallow:
        command += ["-M", "-C"]
    command += [commit, "--", path]
    with utils.workdir(root):
        try:
            res = utils.run_command(command)
        # This means we hit some binary, etc.
        except:
            return {"empty": "%s-%s" % (commit, path)}

    # Do not continue if there is any error
    if res["return_code"] != 0:
        return {"empty": "%s-%s" % (commit, path)}

    # This is the raw git blame
    items = parse_blame_output(res["message"].strip(), path)
    if not items:
        return {"empty": "%s-%s" % (commit, path)}

    # Structure in cache mirrors structure of repo
    utils.mkdir_p(os.path.dirname(tmp_file))
    utils.write_json(items, tmp_file)
    os.rename(tmp_file, save_to)
    return {"output": items, "path": path, "exist": False, "empty": ""}


def parse_blame_output(output, path):
    """
    Helper function to parse blame output and return list.
    """
    # Search each line in output, derive commits, authors, and text
    items = {}
    item = {}
    for line in output.split("\n"):

        for pattern_type, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                item[pattern_type] = match.group(1)

        # We've parsed a single item - save complete time information etc
        if all(key in item for key in ("commit", "author", "text", "time")):

            # Don't include empty lines
            if item["text"].strip() == "":
                item = {}
                continue
            item.update({"path": path})

            # We don't convert time to int here because it gets loaded as str
            current = items
            for key in ["author", "path", "commit"]:
                if item[key] not in current:
                    current[item[key]] = {}
                current = current[item[key]]

            if item["time"] not in current:
                current[item["time"]] = 0
            current[item["time"]] += 1
            item = {}

    return items


class GitParser:
    """
    Shared functions to parse git repos, etc.
    """

    def git(self, *cmd):
        """
        Run a git command (in context of the root)
        """
        with utils.workdir(self.root):
            res = utils.run_command(cmd)
            if res["return_code"] != 0:
                logger.exit(
                    "Issue with command %s: %s" % (" ".join(cmd), res["message"])
                )
            return res["message"].strip()


class CommitStats(GitParser):
    """
    Stats for a particular commit, saved to a cache.
    """

    def __init__(self, root, commit, paths, outdir, shallow=False):
        self.paths = paths
        self.commit = commit
        self.items = {}
        self.root = root
        self.shallow = shallow

        # This is a shared cache of blame output
        self.outdir = outdir
        self.tasks = ()
        self.prepare()

    @property
    def ntasks(self):
        return len(self.tasks)

    @property
    def empty_file(self):
        return os.path.join(self.outdir, ".citelang-empty-results.txt")

    def prepare(self):
        """
        Prepare the list of things to parse. We do this to get a count in advance.
        """
        # We need to take intersection of files for commit and those in paths
        files = self.git(
            "git", "ls-tree", "-r", "--name-only", "--full-tree", self.commit
        ).split("\n")

        if self.paths:
            files = [x for x in files if x in self.paths]

        # A listing of known empty commit-path combos
        self.empties = set()
        if os.path.exists(self.empty_file):
            [
                self.empties.add(x.strip())
                for x in utils.read_file(self.empty_file).split("\n")
            ]

        # Prepare args for imap unordered pool
        self.tasks = [
            (
                self.root,
                self.commit,
                f,
                os.path.join(self.outdir, f, f"{self.commit}.json"),
                self.shallow,
            )
            for f in set(files)
            if "%s-%s" % (self.commit, f) not in self.empties
        ]

    def run(self, pool, complete, total):
        """
        Run git blame to derive stats for the commit and paths, use pool.
        """
        seen = set()
        results = pool.imap_unordered(blame_task, self.tasks)
        for result in results:
            pad = utils.get_terminal_pad(25)
            print("Done {:.2f} %".format(complete / total * 100).ljust(pad), end="\r")
            complete += 1

            # No result - record to empty so we don't try again
            empty = result["empty"]
            if empty:
                self.empties.add(empty)
                continue

            output = result["output"]
            path = result["path"]

            if path not in seen and not result["exist"]:
                seen.add(path)

            # This includes all commits found in the blame over time
            self.items = utils.update_nested(self.items, output)

        # Save empties to file
        utils.write_file("\n".join(list(self.empties)), self.empty_file)


class ContributionSummary:
    """
    A summary of contributions by author, line, file, etc.
    """

    def __init__(self, history, start_timestamp=None, end_timestamp=None):
        self.history = history

        # If we are filtering git blame to within a range
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp

    def iter_items(self, filters=None):
        """
        Yield authors and paths from the history, ensuring that a duplicate
        result from a git blame (a commit persisting across time) does not get
        counted twice.
        """
        filters = utils.read_yaml(filters) if filters else {}
        authors = filters.get("authors", {})
        ignore_files = filters.get("ignore_files", [])
        ignore_basename = filters.get("ignore_basename", [])
        ignore_users = filters.get("ignore_users", [])
        ignore_bots = filters.get("ignore_bots", False)

        seen = set()
        for commit, items in self.history.items():
            for author, paths in items.items():
                for path, commits in paths.items():

                    # ignore specific paths
                    if (
                        os.path.basename(path) in ignore_basename
                        or path in ignore_files
                    ):
                        continue

                    for commit, times in commits.items():
                        for timestamp, count in times.items():

                            # **important** do not count a contribution more than once
                            timestamp = int(timestamp)
                            uid = (commit, author, path, timestamp)
                            if uid in seen:
                                continue
                            seen.add(uid)

                            # Don't include this commit, too early
                            if (
                                self.start_timestamp
                                and int(timestamp) < self.start_timestamp
                            ):
                                continue

                            # Or too late!
                            if (
                                self.end_timestamp
                                and int(timestamp) > self.end_timestamp
                            ):
                                continue

                            # Apply filters here
                            original_author = author
                            if author in authors:
                                author = authors[author]

                            # Is it a bot or do we choose to ignore?
                            if (
                                ignore_bots
                                and "[bot]" in author
                                or author in ignore_users
                                or original_author in ignore_users
                            ):
                                continue

                            yield commit, author, path, int(timestamp), count

    def by_file(self, detail=True, filters=None):
        """
        Return summary of contributions by path
        """
        paths = {}
        for _, author, path, _, count in self.iter_items(filters):

            # Detailed returns results by author
            if detail:
                if path not in paths:
                    paths[path] = {}
                paths[path][author] = count

            # Or just total lines per path
            else:
                if path not in paths:
                    paths[path] = 0
                paths[path] += count

        return self._to_list(paths, detail)

    def by_author(self, detail=True, filters=None):
        """
        Return summary of contributions by author
        """
        results = {}
        for _, author, path, _, count in self.iter_items(filters):

            # Detailed returns results by filename
            if detail:
                if author not in results:
                    results[author] = {}
                results[author][path] = count

                # Or just total lines per author
            else:
                if author not in results:
                    results[author] = 0
                results[author] += count

        # Ensure we are sorted, and parse into list
        return self._to_list(results, detail)

    def _to_list(self, original, detail):
        """
        Convert an original dict (or nested dict) into a list.
        """
        items = []
        if detail:
            for author, paths in original.items():
                sorted_paths = {
                    k: v
                    for k, v in sorted(
                        paths.items(), key=lambda item: item[1], reverse=True
                    )
                }
                items.append({"name": author, "paths": sorted_paths})
        else:
            original = {
                k: v
                for k, v in sorted(
                    original.items(), key=lambda item: item[1], reverse=True
                )
            }
            for author, count in original.items():
                items.append({"name": author, "count": count})
        return items


class ContributionParser(GitParser):
    def __init__(self, root=None, start=None, end=None, outdir=None, paths=None):
        self.start = start
        self.end = end
        self.set_root(root)
        self.set_paths(paths)
        self.outdir = outdir or os.path.join(os.getcwd(), ".contrib")
        utils.mkdir_p(self.outdir)

    @property
    def git_root(self):
        return os.path.join(self.root, ".git")

    @property
    def name(self):
        """
        The repository name
        """
        return os.path.basename(self.root)

    def set_root(self, root):
        """
        Ensure the root exists and set on the class
        """
        root = os.path.abspath(root or os.getcwd())
        if not os.path.exists(root):
            logger.exit(f"{root} does not exist.")
        self.root = root

    def set_paths(self, prefixes=None):
        """
        Parse the repository and set list of paths to include
        """
        paths = set()
        prefixes = prefixes or []
        regex = "(%s)" % "|".join(prefixes) if prefixes else ""

        if not prefixes:
            self.paths = []
            return

        # Get all files in the commit history
        for path in self.git(
            "git", "log", "--pretty=format:", "--name-only", "--diff-filter=A"
        ).split("\n"):
            path = path.strip()
            if not path:
                continue
            if prefixes and re.search(regex, path):
                paths.add(path)
            elif not prefixes:
                paths.add(path)

        self.paths = list(paths)

    def parse(self, return_summary=True, within_range=True, shallow=False):
        """
        Parse the contributions. If within_range is True, don't include git
        blame that goes outside of the range provided.
        """
        # We must be in a git repository
        if not os.path.exists(self.git_root):
            logger.exit(f"Cannot find .git repo in {self.root}")

        # get commits associated with start to end
        commits = self.get_commit_range(shallow)

        # Retrieve items of history
        history = self.index_history(commits, shallow=shallow)

        # Do we want to only include within a range?
        start_timestamp = (
            None if not within_range else self.get_commit_timestamp(commits[0])
        )
        end_timestamp = (
            None if not within_range else self.get_commit_timestamp(commits[-1])
        )

        # Summarize lines by author
        if return_summary:
            return ContributionSummary(history, start_timestamp, end_timestamp)
        return history

    def get_commit_timestamp(self, commit):
        """
        Return the timestamp of a commit.
        """
        return int(self.git("git", "show", "-s", "--format=%ct", commit))

    def index_history(self, commits, shallow=False):
        """
        index git history.
        """
        # Keep a lookup of commit stats by directory
        parsers = {}

        jobs = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(jobs)

        # Create output cache directory just for blames
        cache = os.path.join(self.outdir, "cache")
        utils.mkdir_p(cache)

        # Cut out early if we have a result cached (based on start and end)
        if self.start and self.end:
            uid = "%s-%s" % (self.start, self.end)
            cached_result = os.path.join(self.outdir, "%s.json" % uid)
            if os.path.exists(cached_result):
                logger.info(f"Loading cached result {cached_result}")
                return utils.read_json(cached_result)

        spins = spinner()
        try:

            # First generatae parsers, count tasks in advance
            total = 0
            print("Preparing all tasks...", end="\r")
            for commit in commits:
                parser = CommitStats(
                    self.root, commit, self.paths, cache, shallow=shallow
                )
                print("Preparing all tasks...%s" % next(spins), end="\r")
                total += parser.ntasks
                parsers[commit] = parser

            # Now run parser which knowledge of total
            complete = 0
            print(f"Found {total} tasks!", end="\r")
            for commit, parser in parsers.items():
                parser.run(pool, complete, total)
                complete += parser.ntasks
        finally:
            pool.terminate()

        stats = {}
        for commit, parser in parsers.items():
            stats[commit] = parser.items

        # Cache the result
        if self.start and self.end:
            uid = "%s-%s" % (self.start, self.end)
            cached_result = os.path.join(self.outdir, "%s.json" % uid)
            utils.write_json(stats, cached_result)
        return stats

    def get_tag_commit(self, tag):
        """
        Given a tag, retrieve the commit for it.
        """
        return self.git("git", "rev-list", "-n", "1", tag)

    def get_commit_range(self, shallow=False):
        """
        Given a start and end, parse and return the commits from git
        """
        if shallow:
            res = self.git("git", "log", "--first-parent", "--all", "--format=%H")

        # Possibly duplications but won't miss any commits
        else:
            res = self.git("git", "log", "--all", "--format=%H")

        # Get commits and timestamps
        commits = [x for x in res.split("\n") if x]

        # No commits?
        if not commits:
            logger.exit("This repository does not have any history.")

        # Need to reverse - end (most recent) is at top!
        commits.reverse()

        # Do we have a start commit or tag?
        start_commit = self.start
        if start_commit:
            if start_commit not in commits:
                start_commit = self.get_tag_commit(start_commit)

        end_commit = self.end
        if end_commit:
            if end_commit not in commits:
                end_commit = self.get_tag_commit(end_commit)

        if not end_commit:
            end_commit = commits[-1]
        if not start_commit:
            start_commit = commits[0]

        # +1 ensures we include the end commit in the range
        commits = commits[commits.index(start_commit) : commits.index(end_commit) + 1]
        logger.info("Found %s commits." % len(commits))
        return commits
