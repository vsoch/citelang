#!/usr/bin/python

import pytest
import os

import citelang.utils as utils
import citelang.main.client as client
import citelang.main.schemas as schemas

here = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "name,filename,deps",
    [
        (
            "python-lib",
            "requirements.txt",
            [
                "pypi",
                "pytest",
                "types",
                "requests",
                "sphinx",
                "babel",
                "docutils",
                "Pygments",
            ],
        ),
        (
            "cpp-lib",
            "CMakeLists.txt",
            [
                "spack",
                "eigen3",
                "openmp",
                "lapack",
                "python",
                "curl",
                "xpat",
                "zlib",
                "CMakeLists.txt",
                "cpp-lib",
            ],
        ),
        (
            "r-lib",
            "DESCRIPTION",
            [
                "cran",
                "rmarkdown",
                "knitr",
                "callr",
                "methods",
                "R",
                "shiny",
            ],
        ),
        (
            "python-lib",
            "setup.py",
            ["pypi", "pybind11", "types", "sphinx", "black"],
        ),
        (
            "go-lib",
            "go.mod",
            ["go-lib"],
        ),
        (
            "npm-lib",
            "package.json",
            ["gulp", "markdown", "mixin", "tape", "readable", "object"],
        ),
        (
            "gemfile-lib",
            "Gemfile",
            ["bundler", "rake", "jekyll", "rouge"],
        ),
    ],
)
def test_package_files(name, filename, deps):
    """
    Test loading custom package files
    """
    cli = client.get_parser(filename=os.path.join(here, "testdata", filename))
    result = cli.gen(name=name)
    content = result.render()
    for string in ["Software Credit", name, filename] + deps:
        assert string in content
    print(content)


@pytest.mark.parametrize(
    "manager,name",
    [
        ("pypi", "requests"),
        ("spack", "caliper"),
        ("github", "singularityhub/singularity-cli"),
    ],
)
def test_package(manager, name, tmp_path):
    """
    Test packages
    """
    cli = client.Client(quiet=False)
    result = cli.package(name=name, manager=manager)
    for prop in schemas.package["required"]:
        assert prop in result.data
    result.print_json()

    outfile = os.path.join(str(tmp_path), "%s.json" % os.path.basename(name))
    result.save(outfile)
    loaded = utils.read_json(outfile)
    assert loaded == result.data
    result.table()


def test_list(tmp_path):
    """
    Test listing package managers
    """
    cli = client.Client(quiet=False)
    result = cli.package_managers()

    # 30 at time of parsing
    assert len(result.data) > 30
    result.print_json()

    outfile = os.path.join(str(tmp_path), "package_managers.json")
    result.save(outfile)
    loaded = utils.read_json(outfile)
    assert loaded == result.data
    result.table()


@pytest.mark.parametrize(
    "manager,name",
    [
        ("pypi", "requests"),
        ("spack", "caliper"),
        ("github", "singularityhub/singularity-cli"),
    ],
)
def test_credit(manager, name, tmp_path):
    """
    Test credit function
    """
    cli = client.Client(quiet=False)
    result = cli.credit(name=name, manager=manager)
    result.print_json()

    outfile = os.path.join(str(tmp_path), "%s.json" % os.path.basename(name))
    result.save(outfile)
    loaded = utils.read_json(outfile)
    assert loaded == result.data
    result.print_result()


@pytest.mark.parametrize("graphtype", [(None), ("cypher"), ("gexf"), ("dot")])
def test_graph(graphtype):
    cli = client.Client(quiet=False)
    cli.graph(name="requests", manager="pypi", fmt=graphtype)
