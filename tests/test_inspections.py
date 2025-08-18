# Name      : test_inspections
# Author    : Patrick Cronin
# Date      : 18/08/2025
# Updated   : 18/08/2025
# Purpose   : Test inspections.py using pytest

import pytest
from flask import Flask, get_flashed_messages

from website.inspections import conditioncheck,lchealthscore, lcpass,PASS_SCORE_THRESHOLD, MIN_PITCH_LENGTH


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "secret"
    return app


def test_conditioncheck_pass_fail_and_invalid_input(app):
    """test condition check pass/fail and an invalid input"""
    with app.test_request_context("/"):

        assert conditioncheck("4") is True
        assert conditioncheck("5") is False

        with pytest.raises(ValueError):
            conditioncheck("not-an-int")

        msgs = get_flashed_messages(with_categories=True)
        assert any(cat == "error" and "condition score" in msg.lower() for cat, msg in msgs)


def test_lchealthscore(app):
    """test lifting chain health score function"""
    with app.test_request_context("/"):
        chain_pitch = MIN_PITCH_LENGTH - 1
        measured_mean = chain_pitch - 1

        score = lchealthscore(measured_mean, chain_pitch)
        expected = (chain_pitch / measured_mean) * 100.0
        assert score == pytest.approx(expected)

        msgs = get_flashed_messages(with_categories=True)
        text = " ".join(m for _, m in msgs).lower()
        assert "must be greater than or equal to minimum" in text
        assert "mean measured pitch length should be greater" in text


def test_lcpass_logic():
    """Test lifting chain pass function logic"""
    assert lcpass(False, 100.0) is False

    assert lcpass(True, PASS_SCORE_THRESHOLD - 1) is False

    assert lcpass(True, PASS_SCORE_THRESHOLD) is True
    assert lcpass(True, PASS_SCORE_THRESHOLD + 1) is True
