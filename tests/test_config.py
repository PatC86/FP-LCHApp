# Name      : test_config
# Author    : Patrick Cronin
# Date      : 18/08/2025
# Updated   : 18/08/2025
# Purpose   : Test config.py using pytest

import importlib
import sys
import pytest

def _import_env_config(monkeypatch, secret_value=None):
    """force clean import config.py in controlled env."""

    if secret_value is None:
        monkeypatch.delenv('SECRET_KEY', raising=False)
    else:
        monkeypatch.setenv('SECRET_KEY', secret_value)

    sys.modules.pop('config', None)
    return importlib.import_module('config')

def test_config_secret_key_read(monkeypatch):
    """make sure config picks up secret key when present"""
    test_config = _import_env_config(monkeypatch, secret_value='3BananaS!')

    assert hasattr(test_config, 'Config')
    assert test_config.Config.SECRET_KEY == '3BananaS!'
    assert test_config.Config.SQLALCHEMY_DATABASE_URI == 'sqlite:///database.db'


