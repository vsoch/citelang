#!/usr/bin/python

import pytest
import os

import citelang.utils as utils
import citelang.main.client as client
import citelang.main.schemas as schemas


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
