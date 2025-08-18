# Name      : test_main
# Author    : Patrick Cronin
# Date      : 18/08/2025
# Updated   : 18/08/2025
# Purpose   : Test main.py using pytest

import sys
import runpy
import types
import logging
import pytest
from _pytest.monkeypatch import monkeypatch


class DummyApp:
    """Light dummy application as stand in for flask app for .run() use"""
    run_called = False
    run_kwargs = False

    def __init__(self, should_raise=None):
        self.should_raise = should_raise

    def run(self, **kwargs):
        DummyApp.run_called = True
        DummyApp.run_kwargs = kwargs
        if self.should_raise:
            raise RuntimeError('oh no!')

@pytest.fixture(autouse=True)
def _reset_state():
    """Reset state after each test"""
    DummyApp.run_called = False
    DummyApp.run_kwargs = None
    sys.modules.pop('main', None)
    yield
    sys.modules.pop('main', None)
    DummyApp.run_called = False
    DummyApp.run_kwargs = None

def _create_dummy_webapp(monkeypatch, create_app_func):
    """Create a dummy web app"""
    dummy= types.SimpleNamespace(create_app=create_app_func)
    monkeypatch.setitem(sys.modules, 'website', dummy)

def test_import_app_creates_but_not_running(monkeypatch):
    """importing of main not as __main__ app should be created but not run"""
    _create_dummy_webapp(monkeypatch, lambda: DummyApp())

    test_globs = runpy.run_module('main', run_name='not_main')

    assert 'app' in test_globs
    assert isinstance(test_globs['app'], DummyApp)
    assert DummyApp.run_called is False

def test_run_app(monkeypatch):
    """Running script should call app.run"""
    _create_dummy_webapp(monkeypatch, lambda: DummyApp())

    runpy.run_module('main', run_name='__main__')

    assert DummyApp.run_called is True
    assert DummyApp.run_kwargs == {"debug": True}

def test_logging_and_exit_code_1(monkeypatch, caplog):
    """if app.run raises, error should be logged and exit(1) occurs"""

    _create_dummy_webapp(monkeypatch, lambda: DummyApp(should_raise='exception'))

    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit) as se:
            runpy.run_module('main', run_name='__main__')

    assert se.value.code == 1
    assert 'Failed to run app' in caplog.text

