#!/usr/bin/python

import os
import shutil
import pytest
import json
import citelang.utils as utils


def test_write_read_files(tmp_path):
    """
    test_write_read_files will test the functions write_file and read_file
    """
    print("Testing utils.write_file...")

    tmpfile = str(tmp_path / "written_file.txt")
    assert not os.path.exists(tmpfile)
    utils.write_file("hello!", tmpfile)
    assert os.path.exists(tmpfile)

    print("Testing utils.read_file...")

    content = utils.read_file(tmpfile)
    assert content == "hello!"


def test_write_bad_json(tmp_path):

    bad_json = {"Wakkawakkawakka'}": [{True}, "2", 3]}
    tmpfile = str(tmp_path / "json_file.txt")
    assert not os.path.exists(tmpfile)
    with pytest.raises(TypeError):
        utils.write_json(bad_json, tmpfile)


def test_write_json(tmp_path):

    good_json = {"Wakkawakkawakka": [True, "2", 3]}
    tmpfile = str(tmp_path / "good_json_file.txt")

    assert not os.path.exists(tmpfile)
    utils.write_json(good_json, tmpfile)
    with open(tmpfile, "r") as f:
        content = json.loads(f.read())
    assert isinstance(content, dict)
    assert "Wakkawakkawakka" in content
    content = utils.read_json(tmpfile)
    assert "Wakkawakkawakka" in content


def test_get_installdir():
    print("Testing utils.get_installdir")

    whereami = utils.get_installdir()
    print(whereami)
    assert whereami.endswith("citelang")


def test_run_command():
    print("Testing utils.run_command")

    result = utils.run_command(["echo", "hello"])
    assert result["message"] == "hello\n"
    assert result["return_code"] == 0


def test_get_tmpdir_tmpfile():
    print("Testing utils.get_tmpdir, get_tmpfile")

    tmpdir = utils.get_tmpdir()
    assert os.path.exists(tmpdir)
    assert os.path.basename(tmpdir).startswith("citelang")
    shutil.rmtree(tmpdir)
    tmpdir = utils.get_tmpdir(prefix="name")
    assert os.path.basename(tmpdir).startswith("name")
    shutil.rmtree(tmpdir)
    tmpfile = utils.get_tmpfile()
    assert "citelang" in tmpfile
    os.remove(tmpfile)
    tmpfile = utils.get_tmpfile(prefix="pancakes")
    assert "pancakes" in tmpfile
    os.remove(tmpfile)


def test_mkdir_p(tmp_path):
    print("Testing utils.mkdir_p")

    dirname = str(tmp_path / "input")
    result = os.path.join(dirname, "level1", "level2", "level3")
    utils.mkdir_p(result)
    assert os.path.exists(result)


def test_print_json():
    print("Testing utils.print_json")

    result = utils.print_json({1: 1})
    assert result == '{\n    "1": 1\n}'
