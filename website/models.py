# NAME: models
# AUTHOR: Patrick Cronin
# Date: 02/08/2025
# Update: 02/08/2025
# Purpose: Define database model for lifting assets, asset class, sites, users, roles
from sqlalchemy import CheckConstraint

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# Class to define assets table, links and constraints
class Assets(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    equip_no = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(50), nullable=False)
    location_on_site = db.Column(db.String(50), nullable=False)
    site_no = db.Column(db.Integer, db.ForeignKey('sites.site_id'), nullable=False)
    equip_status = db.Column(db.String(2), db.ForeignKey('equip_status.status_id'), nullable=False)
    equip_class = db.Column(db.String(2), db.ForeignKey('equip_class.class_id'), nullable=False)
    __table_args__ = (
        CheckConstraint('equip_no BETWEEN 100000000000 AND 999999999999999', name='equip_no_12_digits'),
    )


class Sites(db.Model):
    __tablename__ = 'sites'
    id = db.Column(db.Integer, primary_key=True)
    site_no = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(50), nullable=False)
    __table_args__ = (
        CheckConstraint('site_no BETWEEN 100000 and 999999', name='site_no_6_digits'),
    )
    assets = db.relationship('Assets', backref='sites', lazy=True)


class Assetclass(db.Model):
    __tablename__ = 'assetclass'
    class_id = db.Column(db.String(2), primary_key=True)
    class_description = db.Column(db.String(50), nullable=False)
    assets = db.relationship('Assets', backref='assetclass', lazy=True)


class Assetstatus(db.Model):
    __tablename__ = 'assetstatus'
    status_id = db.Column(db.String(2), primary_key=True)
    status_description = db.Column(db.String(50), nullable=False)
    assets = db.relationship('Assets', backref='assetstatus', lazy=True)


class Condition(db.Model):
    __tablename__ = 'condition'
    condition_id = db.Column(db.Integer, primary_key=True)
    condition_code = db.Column(db.String(2), nullable=False)
    condition_description = db.Column(db.String(50), nullable=False)
