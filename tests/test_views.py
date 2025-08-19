# Name      : test_views
# Author    : Patrick Cronin
# Date      : 18/08/2025
# Updated   : 18/08/2025
# Purpose   : Test views.py using pytest

import sys
import types
import importlib
import pytest
from flask import Flask
from flask_login import LoginManager

class _QueryChain:
    def filter_by(self, **kwargs):
        return self
    def filter(self, *args, **kwargs):
        return self
    def all(self):
        return []


class _SessionStub:
    def __init__(self): self._q = _QueryChain()
    def query(self, *args, **kwargs): return self._q


def _make_logged_in_app(views_mod, user_id=1, user_role="FIELD"):
    app = Flask(__name__)
    app.secret_key = "secret"

    lm = LoginManager()
    lm.init_app(app)

    class _DummyUser:
        def __init__(self, uid, role):
            self.id = uid
            self.user_role = role
        def get_id(self): return str(self.id)
        @property
        def is_authenticated(self): return True

    users = {str(user_id): _DummyUser(user_id, user_role)}

    @lm.user_loader
    def _load(uid): return users.get(uid)

    app.register_blueprint(views_mod.views)
    client = app.test_client()

    with client.session_transaction() as s:
        s["_user_id"], s["_fresh"] = str(user_id), True

    return app, client


@pytest.fixture
def views_with_render_capture(monkeypatch):
    sys.modules.pop('website.views', None)
    sys.modules.pop('website.models', None)
    views_mod = importlib.import_module("website.views")

    holder = {}
    def _capture(template_name, **ctx):
        holder["template"] = template_name
        holder["ctx"] = ctx
        return f"OK:{template_name}"

    monkeypatch.setattr(views_mod, "render_template", _capture, raising=True)
    return views_mod, holder


def test_faqs_renders_template(views_with_render_capture):
    views_mod, holder = views_with_render_capture
    app = Flask(__name__)
    app.secret_key = "secret"
    app.register_blueprint(views_mod.views)
    client = app.test_client()

    resp = client.get("/faqs")
    assert resp.status_code == 200
    assert holder["template"] == "faqs.html"


def test_inspection_get_renders_template_with_minimal_lists(monkeypatch, views_with_render_capture):
    views_mod, holder = views_with_render_capture

    db_stub = types.SimpleNamespace(session=_SessionStub())
    monkeypatch.setattr(views_mod, "db", db_stub, raising=True)

    app, client = _make_logged_in_app(views_mod, user_role="FIELD")
    resp = client.get("/inspection")

    assert resp.status_code == 200
    assert holder["template"] == "inspection.html"
    for i in ("min_length", "max_length", "min_pitch_length",
              "max_pitch_length", "min_pitches_measured",
              "lifting_chain_list", "condition_list", "other_asset_list"):
        assert i in holder["ctx"]


def test_inspection_post_missing_fields_redirects(monkeypatch, views_with_render_capture):
    views_mod, _holder = views_with_render_capture
    app, client = _make_logged_in_app(views_mod, user_role="FIELD")

    resp = client.post("/inspection", data={"form": "chain_insp", "equip_no": "123"}, follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/inspection")


def test_home_field_user_renders_template(monkeypatch, views_with_render_capture):
    views_mod, holder = views_with_render_capture

    class _InspQuery:
        def filter_by(self, **kwargs): return self
        def all(self): return []
    class _Inspection: pass
    _Inspection.query = _InspQuery()
    monkeypatch.setattr(views_mod, "Inspection", _Inspection, raising=True)

    app, client = _make_logged_in_app(views_mod, user_role="FIELD")
    resp = client.get("/")

    assert resp.status_code == 200
    assert holder["template"] == "home.html"
    assert "inspections" in holder["ctx"]
    assert holder["ctx"]["inspections"] == []
