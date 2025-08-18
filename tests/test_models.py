# Name      : test_models
# Author    : Patrick Cronin
# Date      : 18/08/2025
# Updated   : 18/08/2025
# Purpose   : Test models.py using pytest

import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError

import website
from website import models as m


@pytest.fixture
def app():
    """lite flask app for tests"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    website.db.init_app(app)

    with app.app_context():
        website.db.create_all()
        yield app
        website.db.session.rollback()
        website.db.drop_all()


@pytest.fixture
def session(app):
    return website.db.session


def _dummy_data(session):
    """dummy data for testing foreign keys"""
    role = m.Role(role_name='ADMIN', role_description='Administrator')
    user = m.User(username='goffj', first_name='Jared', surname='Goff',
                  password='hashed', user_role='ADMIN')
    site = m.Site(site_no=123456, description='Calm Lands WPS')
    assetclass = m.Assetclass(class_id='XX', class_description='Trampoline')
    assetstatus = m.Assetstatus(status_id='XX', status_description='NOT GREAT')

    session.add_all([role, user, site, assetclass, assetstatus])
    session.flush()
    return role, user, site, assetclass, assetstatus

def test_models_link(session):
    role, user, site, assetclass, assetstatus = _dummy_data(session)
    asset = m.Asset(equip_no=123456789123, description='Basset', location_on_site='somewhere', site_no=site.id, equip_status=assetstatus.status_id, equip_class=assetclass.class_id)
    condition = m.Condition(condition_code='A1', condition_description='TOP NOTCH')
    session.add_all([asset, condition])
    session.flush()

    inspection = m.Inspection(equip_no=asset.equip_no, condition_code=condition.condition_code, chain_length=10, chain_pitch_length=100, measure_mean_pitch_length=100, pitches_measured=15, lc_health_score=100, asset_passed=True, user_id=user.id)
    session.add(inspection)
    session.commit()

    x = m.Asset.query.filter_by(equip_no=asset.equip_no).one()
    assert len(x.inspections) == 1
    assert x.inspections[0].id == inspection.id
    assert x.site.id == site.id

    y = m.Inspection.query.get(inspection.id)
    assert y.asset.equip_no == asset.equip_no
    assert y.user.id == user.id
    assert y.condition.condition_code == condition.condition_code

    z = m.User.query.get(user.id)
    assert len(z.inspections) == 1
    assert z.role.role_name == role.role_name

def test_asset_equip_no_constraint(session):
    _, _, site, assetclass, assetstatus = _dummy_data(session)
    fail_asset = m.Asset(equip_no=1, description='long no chain', location_on_site='somewhere', site_no=site.id, equip_status=assetstatus.status_id, equip_class=assetclass.class_id)
    session.add(fail_asset)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

def test_asset_equip_no_unique(session):
    """test creation of dublicate equip_no in asset table will raise error and not add to db."""
    _, _, site, assetclass, assetstatus = _dummy_data(session)
    asset1 = m.Asset(
        equip_no=111111111111,
        description='Chain X',
        location_on_site='Rack 1',
        site_no=site.id,
        equip_status=assetstatus.status_id,
        equip_class=assetclass.class_id,
    )
    session.add(asset1)
    session.commit()

    asset2 = m.Asset(
        equip_no=111111111111,
        description='Chain Y',
        location_on_site='Rack 2',
        site_no=site.id,
        equip_status=assetstatus.status_id,
        equip_class=assetclass.class_id,
    )
    session.add(asset2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

