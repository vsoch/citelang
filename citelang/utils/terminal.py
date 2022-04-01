__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"


from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from .fileio import get_tmpdir
import os


def get_installdir():
    """get_installdir returns the installation directory of the application"""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def clone(name):
    """
    Clone a repository by name
    """
    tmpdir = get_tmpdir()
    res = run_command(
        ["git", "clone", "--depth", "1", f"https://github.com/{name}", tmpdir]
    )

    # Don't fail entire process, just can't get dependencies
    if res["return_code"] != 0:
        return
    return tmpdir


def run_command(cmd, sudo=False, stream=False):
    """run_command uses subprocess to send a command to the terminal.

    Parameters
    ==========
    cmd: the command to send, should be a list for subprocess
    error_message: the error message to give to user if fails,
    if none specified, will alert that command failed.

    """
    stdout = PIPE if not stream else None
    if sudo is True:
        cmd = ["sudo"] + cmd

    try:
        output = Popen(cmd, stderr=STDOUT, stdout=stdout)

    except FileNotFoundError:
        cmd.pop(0)
        output = Popen(cmd, stderr=STDOUT, stdout=PIPE)

    t = output.communicate()[0], output.returncode
    output = {"message": t[0], "return_code": t[1]}

    if isinstance(output["message"], bytes):
        output["message"] = output["message"].decode("utf-8")

    return output


def get_time_now():
    """
    Get a timestring for the datetime now.
    """
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


def confirm_action(question, force=False):
    """confirm if the user wants to perform a certain action

    Parameters
    ==========
    question: the question that will be asked
    force: if the user wants to skip the prompt
    """
    if force is True:
        return True

    response = input(question)
    while len(response) < 1 or response[0].lower().strip() not in "ynyesno":
        response = input("Please answer yes or no: ")

    if response[0].lower().strip() in "no":
        return False

    return True


def confirm_uninstall(filename, force=False):
    """confirm if the user wants to uninstall a module

    Parameters
    ==========
    filename: the file that will be removed
    force: if the user wants to skip the prompt
    """
    return confirm_action(
        "Are you sure you want to uninstall {}".format(filename), force
    )
