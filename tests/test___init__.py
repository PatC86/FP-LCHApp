# Name      : test__init__
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 18/08/2025
# Purpose   : Test functions defined in __init__

import sys
import types
import logging
import pytest
from flask import Flask, Blueprint

def _dummy_model_module():
    """stand ins for website.models providing the name of the models create_app imports"""
    m = types.ModuleType('website.models')

    class _Query:
        @staticmethod
        def get(n):
            return {'id': n}

    class User:
        pass

    User.query = _Query()

    for classname in ['Role', 'Asset', 'Assetclass', 'Assetstatus', 'Site', 'Condition', 'Inspection']:
        setattr(m, classname, type(classname, (), {}))
    m.User = User
    return m

def _install_sub_modules(*, break_views: bool = False):
    """stands in website.models/views/auth/csp"""
    for module_name in ('website.models', 'website.views', 'website.auth', 'website.csp'):
        sys.modules.pop(module_name, None)

    sys.modules['website.models'] = _dummy_model_module()

    v = types.ModuleType('website.views')
    v.views = object() if break_views else Blueprint('views', __name__)
    sys.modules['website.views'] = v

    a = types.ModuleType('website.auth')
    a.auth = object() if break_views else Blueprint('auth', __name__)
    sys.modules['website.auth'] = a

    c = types.ModuleType('website.csp')
    c.csp = Blueprint('csp', __name__)
    sys.modules['website.csp'] = c

@pytest.fixture(autouse=True)
def _reset_modules():
    """reset modules for each test"""
    sys.modules.pop('website', None)
    yield
    for module_name in ('website.models', 'website.views', 'website.auth', 'website.csp'):
        sys.modules.pop(module_name, None)
    sys.modules.pop('website', None)

@pytest.fixture(autouse=True)
def _test_secret_key(monkeypatch):
    """Dummy SECRET_KEY for testing"""
    monkeypatch.setenv('SECRET_KEY', 'secret')
    yield

def test_create_app_registers_blueprints():
    """test blueprints are registered when Flask aspp created"""
    import website
    _install_sub_modules(break_views=False)

    app = website.create_app()

    assert isinstance(app, Flask)
    assert 'views' in app.blueprints
    assert 'auth' in app.blueprints
    assert 'csp' in app.blueprints

def test_init_app_failure(monkeypatch, caplog):
    """Test logging raising of exception in initialisation of application"""
    import website
    _install_sub_modules(break_views=False)

    def fail(_app):
        raise RuntimeError('Failed init')

    monkeypatch.setattr(website.db, "init_app", fail)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            website.create_app()

    assert 'Error while creating app:' in caplog.text

def test_blueprint_reg_failure(caplog):
    """test if when blueprint registration fails. log should be created."""
    import website
    _install_sub_modules(break_views=True)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception):
            website.create_app()

    assert 'Failed during blueprint setups:' in caplog.text

def test_login_manager_failure(monkeypatch, caplog):
    """Test logging raising of exception in login_manager init failure"""
    import website
    _install_sub_modules(break_views=False)

    class DummyLoginManager:
        def __init__(self):
            self.login_view = None

        def init_app(self, _app):
            raise RuntimeError('Login init failed')

        def user_loader(self, fn):
            return fn

    monkeypatch.setattr(website, "LoginManager", DummyLoginManager)
    with caplog.at_level(logging.ERROR):
        app = website.create_app()

    assert app is None
    assert 'Failed to load user' in caplog.text

def test_user_loader_failure(monkeypatch, caplog):
    """Test logging raising of exception in user_loader failing to load user"""
    import website
    _install_sub_modules(break_views=False)

    class DummyLoginManager:
        def __init__(self):
            self.login_view = None

        def init_app(self, _app):
            pass

        def user_loader(self, fn):
            raise RuntimeError('User Loader failed')

    monkeypatch.setattr(website, "LoginManager", DummyLoginManager)
    with caplog.at_level(logging.ERROR):
        app = website.create_app()

    assert app is None
    assert 'Failed to load user' in caplog.text
