# Name      : test_userrolewrappers
# Author    : Patrick Cronin
# Date      : 18/08/2025
# Updated   : 18/08/2025
# Purpose   : Test userrolewrappers.py using pytest

import pytest
from flask import Flask, Blueprint
from flask_login import LoginManager
from website.userrolewrappers import admin_required

class _TestUser:
    def __init__(self, uid):
        self.id = uid

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

def _create_app_with_user(user):
    app = Flask(__name__)
    app.secret_key = 'super secret key'

    auth_bp = Blueprint('auth', __name__)

    @auth_bp.route('/login')
    def login():
        return 'LOGIN'

    app.register_blueprint(auth_bp)

    lm = LoginManager()
    lm.init_app(app)
    _store = {str(user.id): user}

    @lm.user_loader
    def load(uid):
        return _store.get(uid)

    @app.route('/admin_only')
    @admin_required
    def admin_only():
        return 'ADMIN ONLY'

    return app

def test_admin_dec_allows_admin_user(monkeypatch):
    """admin user should be allowed access to blueprint with admin_required decorator"""
    user = _TestUser(uid=7)
    user.user_role = 'ADMIN'

    app = _create_app_with_user(user)
    client = app.test_client()

    with client.session_transaction() as sesh:
        sesh['_user_id'] = user.get_id()
        sesh['_fresh'] = True

    resp = client.get('/admin_only')
    assert resp.status_code == 200
    assert resp.data == b'ADMIN ONLY'

def test_non_admin_redirects(monkeypatch):
    """non-admin user should redirect to auth login page"""
    user = _TestUser(uid=8)

    app = _create_app_with_user(user)
    client = app.test_client()

    with client.session_transaction() as sesh:
        sesh['_user_id'] = user.get_id()
        sesh['_fresh'] = True

    resp = client.get('/admin_only', follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/login')

    with client.session_transaction() as sesh:
        flashes = sesh.get('_flashes', [])
    assert any('Please retry' in msg for _, msg in flashes)
