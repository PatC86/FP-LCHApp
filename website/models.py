# NAME: models
# AUTHOR: Patrick Cronin
# Date: 02/08/2025
# Update: 18/08/2025
# Purpose: Define model for assets, asset class, asset status, condition, inspections, sites, users and roles
from sqlalchemy import CheckConstraint

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# Class to define assets model, table, links and constraints
class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    equip_no = db.Column(db.Integer, nullable=False, unique=True)
    description = db.Column(db.String(50), nullable=False)
    location_on_site = db.Column(db.String(50), nullable=False)
    site_no = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    equip_status = db.Column(db.String(2), db.ForeignKey('assetstatus.status_id'), nullable=False)
    equip_class = db.Column(db.String(2), db.ForeignKey('assetclass.class_id'), nullable=False)
    inspections = db.relationship('Inspection', backref='asset', lazy=True)
    __table_args__ = (
        CheckConstraint('equip_no BETWEEN 100000000000 AND 999999999999999', name='equip_no_12_digits'),
    )


# class to define inspections model, tables, links and constraints.
class Inspection(db.Model):
    __tablename__ = 'inspection'
    id = db.Column(db.Integer, primary_key=True)
    equip_no = db.Column(db.Integer, db.ForeignKey('asset.equip_no'), nullable=False)
    condition_code = db.Column(db.String(2), db.ForeignKey('condition.condition_code'), nullable=False)
    chain_length = db.Column(db.Float)
    chain_pitch_length = db.Column(db.Integer)
    measure_mean_pitch_length = db.Column(db.Integer)
    pitches_measured = db.Column(db.Integer)
    lc_health_score = db.Column(db.Integer)
    asset_passed = db.Column(db.Boolean)
    insp_date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# class to define user model, tables, links and constraints.
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(10), db.ForeignKey('role.role_name'), nullable=False)
    inspections = db.relationship('Inspection', backref='user', lazy=True)


# class to define site model, tables, links and constraints.
class Site(db.Model):
    __tablename__ = 'site'
    id = db.Column(db.Integer, primary_key=True)
    site_no = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(50), nullable=False)
    __table_args__ = (
        CheckConstraint('site_no BETWEEN 100000 and 999999', name='site_no_6_digits'),
    )
    assets = db.relationship('Asset', backref='site', lazy=True)


# class to define asset class model, tables, links and constraints.
class Assetclass(db.Model):
    __tablename__ = 'assetclass'
    class_id = db.Column(db.String(2), primary_key=True)
    class_description = db.Column(db.String(50), nullable=False)
    asset = db.relationship('Asset', backref='assetclass', lazy=True)


# class to define asset status model, tables, links and constraints.
class Assetstatus(db.Model):
    __tablename__ = 'assetstatus'
    status_id = db.Column(db.String(2), primary_key=True)
    status_description = db.Column(db.String(50), nullable=False)
    asset = db.relationship('Asset', backref='assetstatus', lazy=True)


# class to define condition model, tables, links and constraints.
class Condition(db.Model):
    __tablename__ = 'condition'
    condition_code = db.Column(db.String(2), primary_key=True)
    condition_description = db.Column(db.String(50), nullable=False)
    inspection = db.relationship('Inspection', backref='condition', lazy=True)


# class to define role model, tables, links and constraints.
class Role(db.Model):
    __tablename__ = 'role'
    role_name = db.Column(db.String(10), primary_key=True)
    role_description = db.Column(db.String(50), nullable=False)
    users = db.relationship('User', backref='role', lazy=True)
