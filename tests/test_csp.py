# Name      : test_csp
# Author    : Patrick Cronin
# Date      : 18/08/2025
# Updated   : 18/08/2025
# Purpose   : Test csp.py using pytest

import pytest
from flask import Flask
from website.csp import csp, CSP_POLICY

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(csp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_csp_header_blueprint(client):
    """test blueprint adds csp header"""
    resp = client.post('/cspreport', json={'csp-report': {'blocked uri': 'inline'}})

    header = resp.headers.get('Content-Security-Policy-Report-Only')
    assert header is not None
    assert isinstance(header, str)
    assert "default-src 'self';" in header
    assert "script-src 'self';" in header

def test_csp_returns_records_and_204(client, capsys):
    """test creation of report records and returning 204"""
    record = {"csp-report": {"document-uri": "https//kittens.com", "blocked-uri": "inline"}}
    resp = client.post('/cspreport', json=record)

    assert resp.status_code == 204
    out, _ = capsys.readouterr()
    assert 'Violations:' in out


