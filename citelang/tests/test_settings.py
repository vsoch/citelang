#!/usr/bin/python

import os

from citelang.main.settings import Settings

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)


def test_environment_substitution(tmp_path):
    """
    Test variable substitution
    """
    settings_file = os.path.join(root, "settings.yml")
    settings = Settings(settings_file)

    assert "pancakes" not in settings.cache_dir
    assert "cache" in settings.cache_dir
    os.environ["SOME_PATH"] = "/tmp"
    os.putenv("SOME_PATH", "/tmp")
    settings.set("cache_dir", "$SOME_PATH/pancakes")
    assert settings.cache_dir == "/tmp/pancakes"


def test_set_get(tmp_path):
    """
    Test variable set/get
    """
    settings_file = os.path.join(root, "settings.yml")
    settings = Settings(settings_file)
    assert settings.cache_dir.endswith("cache")
    settings.set("cache_dir", "/tmp/cache")
    assert settings.cache_dir == "/tmp/cache"
