# Name      : test_auth
# Author    : Patrick Cronin
# Date      : 18/08/2025
# Updated   : 18/08/2025
# Purpose   : Test auth.py using pytest

import sys
import types
import importlib
import pytest
from flask import Flask, Blueprint
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from website.inspections import PASS_SCORE_THRESHOLD


class SessionStub:
    def __init__(self):
        self.added = []
        self.committed = False
        self.rolled_back = False

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def query(self, *args, **kwargs):
        return _QueryChainStub()

class _QueryChainStub:
    def join(self, *args, **kwargs):
        return self

    def all(self):
        return []

def _install_admin_decorator():
    """importing of a passthrough decorator for @admin_required decorated function"""
    sys.modules.pop('website.userrolewrappers', None)
    aw = types.ModuleType('website.userrolewrappers')

    def admin_required(fn):
        return fn

    aw.admin_required = admin_required
    sys.modules['website.userrolewrappers'] = aw

def _stub_models_module():
    """placeholder models for User and Role models for auth"""
    sys.modules.pop('website.models', None)
    m = types.ModuleType('website.models')

    class User:
        pass

    class Role:
        pass

    m.User = User
    m.Role = Role
    sys.modules['website.models'] = m

@pytest.fixture
def flask_app(monkeypatch):
    """Build lite version of flask app"""
    _install_admin_decorator()
    _stub_models_module()

    import website
    db_stub = types.SimpleNamespace(session=SessionStub())
    monkeypatch.setattr(website, 'db', db_stub, raising=True)

    sys.modules.pop('website.auth', None)
    auth_mod = importlib.import_module('website.auth')

    monkeypatch.setattr(auth_mod, 'render_template', lambda template_name, **ctx: f'OK: {template_name}', raising=True)

    app = Flask(__name__)
    app.secret_key = 'testing'

    lm = LoginManager()
    lm.init_app(app)

    @lm.user_loader
    def _load(uid):
        return None

    views_bp = Blueprint('views', __name__)

    @views_bp.route('/')
    def home():
        return 'HOME'

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_mod.auth)

    return app, app.test_client(), auth_mod, db_stub

def test_login_success(flask_app, monkeypatch):
    app, client, auth_mod, _db = flask_app

    class DummyUser:
        def __init__(self, username, password_hash):
            self.id = 1
            self.username = username
            self.password = password_hash
            self.is_active = True

        def get_id(self):
            return str(self.id)

    class StubQuery:
        def filter_by(self, **kwargs):
            self.kw = kwargs
            return self

        def first(self):
            if self.kw.get('username') == 'jimbob3':
                return DummyUser('jimbob3', generate_password_hash('jimbobr0x'))
            return None

    DummyUser.query = StubQuery()
    monkeypatch.setattr(auth_mod, "User", DummyUser, raising=True)

    resp = client.post('/login', data={'username': 'jimbob3', 'password': 'jimbobr0x'}, follow_redirects=False)

    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/')

def test_login_failure(flask_app, monkeypatch):
    app, client, auth_mod, _db = flask_app

    class DummyUser:
        def __init__(self, username, password_hash):
            self.id = 2
            self.username = username
            self.password_hash = password_hash
            self.is_active = True

        def get_id(self):
            return str(self.id)

    class StubQuery:
        def filter_by(self, **kwargs):
            self.kw = kwargs
            return self

    def first(self):
        if self.kw.get('username') == 'gilly2':
            return DummyUser('gilly2', generate_password_hash('gillygul!'))
        return None

    DummyUser.query = StubQuery()
    monkeypatch.setattr(auth_mod, "User", DummyUser, raising=True)

    resp = client.post('/login', data={'username': 'gilly2', 'password': 'INCORRECT'}, follow_redirects=False)

    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/login')

def test_logout(flask_app, monkeypatch):
    app, client, auth_mod, _db = flask_app

    class DummyUser:
        def __init__(self, username, password_hash):
            self.id = 4
            self.username = username
            self.password = password_hash
            self.is_active = True

        def get_id(self):
            return str(self.id)

    class StubQuery:
        def filter_by(self, **kwargs):
            self.kw = kwargs
            return self

        def first(self):
            if self.kw.get('username') == 'clarksonk':
                return DummyUser('clarksonk', generate_password_hash('s1nceubeeng0ne!'))
            return None

    DummyUser.query = StubQuery()
    monkeypatch.setattr(auth_mod, "User", DummyUser, raising=True)

    resp = client.post('/login', data={'username': 'clarksonk', 'password': 's1nceubeeng0ne!'}, follow_redirects=False)
    assert resp.status_code == 302

    with client.session_transaction() as sesh:
        assert '_user_id' in sesh
        assert sesh['_user_id'] == '4'

    lm = getattr(app, 'login_manager', None or app.extensions.get('login_manager'))

    @lm.user_loader
    def _load(uid):
        class _U:
            def __init__(self, _id):
                self.id = int(_id)
                self.is_active = True

            def get_id(self):
                return str(self.id)

            @property
            def is_authenticated(self):
                return True
        return _U(uid)

    resp = client.get('/logout', follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/login')

    with client.session_transaction() as sesh:
        assert '_user_id' not in sesh

def test_user_creation(flask_app, monkeypatch):
    app, client, auth_mod, db_stub = flask_app
    class Role:
        role_name = 'ADMIN'
        role_description = 'Administrator'

    monkeypatch.setattr(auth_mod, 'Role', Role, raising=True)

    createduser = {}

    class DummyUser:
        def __init__(self, username, first_name, surname, user_role, password):
            createduser.update({
                'username': username,
                'first_name': first_name,
                'surname': surname,
                'user_role': user_role,
                'password': password
            })
            self.username = username
            self.first_name = first_name
            self.surname = surname
            self.user_role = user_role
            self.password = password

    class StubQuery:
        def filter_by(self, **kwargs):
            self.kw = kwargs
            return self

        def first(self):
            return None

    DummyUser.query = StubQuery()
    monkeypatch.setattr(auth_mod, "User", DummyUser, raising=True)

    resp = client.post('/useradmin', data={"username": "ketchuma",
                                                "first_name": "Ash",
                                                "surname": "Ketchum",
                                                "role": "FIELD",
                                                "password1": "catchemall!",
                                                "password2": "catchemall!"}, follow_redirects=False)

    assert resp.status_code == 200
    assert len(db_stub.session.added) == 1
    assert db_stub.session.committed is True
    assert createduser['password'] != 'catchemall!'