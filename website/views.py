# Name      : views
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 17/08/2025
# Purpose   : Define views for application

from flask import Blueprint, render_template, flash, url_for, request
from flask_login import current_user, login_required
from werkzeug.utils import redirect
from sqlalchemy import select

from . import db
from .userrolewrappers import admin_required
from .inspections import conditioncheck, lchealthscore, lcpass, MIN_CHAIN_LENGTH, MAX_CHAIN_LENGTH, MIN_PITCH_LENGTH, \
    MAX_PITCH_LENGTH, MIN_PITCHES_MEASURED

from website.models import Site, Asset, Assetclass, Assetstatus, User, Role, Inspection, Condition as ConditionModel

views = Blueprint('views', __name__)


# flask blueprint view for home page
@views.route('/')
@login_required
def home():
    if current_user.user_role == 'ADMIN':
        UserCount = User.query.count()
        AdminCount = User.query.filter_by(user_role='ADMIN').count()
        ContEngCount = User.query.filter_by(user_role='CONTENG').count()
        FieldCount = User.query.filter_by(user_role='FIELD').count()
        InspCount = Inspection.query.count()
        Counts = (UserCount, AdminCount, ContEngCount, FieldCount, InspCount)
        return render_template('home.html', user=current_user, counts=Counts)
    elif current_user.user_role == 'CONTENG':
        FailedInsps = db.session.query(Inspection.id, Inspection.equip_no, Inspection.user_id, Inspection.insp_date,
                                       Inspection.condition_code, Inspection.lc_health_score, Inspection.asset_passed,
                                       Asset.equip_class, Asset.site_no, Assetclass.class_description, Site.description,
                                       User.first_name, User.surname).join(Asset,
                                                                           Inspection.equip_no == Asset.equip_no).join(
            Assetclass, Asset.equip_class == Assetclass.class_id).join(Site, Asset.site_no == Site.site_no).join(User,
                                                                                                                 Inspection.user_id == User.id).filter(
            Inspection.asset_passed.is_(False)).all()
        print(FailedInsps)
        return render_template('home.html', user=current_user, failedinsps=FailedInsps)
    elif current_user.user_role == 'FIELD':
        Inspections = Inspection.query.filter_by(user_id=current_user.id).all()
        return render_template('home.html', user=current_user, inspections=Inspections)
    else:
        return render_template('home.html', user=current_user)


# flask blueprint view for FAQs
@views.route('faqs')
def faqs():
    return render_template('faqs.html', user=current_user)


# flask blueprint view for operational sites
@views.route('/sites')
@login_required
def sites():
    SiteList = db.session.query(Site).all()
    return render_template('sites.html', user=current_user, sites=SiteList)


# flask blueprint view for lifting assets
@views.route('/assets')
@login_required
def assets():
    AssetList = db.session.query(Asset.equip_no, Asset.description, Asset.location_on_site,
                                 Assetclass.class_description, Assetstatus.status_description,
                                 Site.description.label('site_desc')).join(
        Assetclass,
        Asset.equip_class == Assetclass.class_id).join(
        Assetstatus, Asset.equip_status == Assetstatus.status_id).join(Site, Asset.site_no == Site.site_no).all()
    return render_template('assets.html', user=current_user, assets=AssetList)


# blueprint view for inspections (lifting chain and other lifting assets)
@views.route('/inspection', methods=['GET', 'POST'])
@login_required
def inspection():
    if request.method == 'POST':
        form_id = request.form.get('form')
        # processing inspections for lifting assets that aren't lifting chains
        if form_id == 'other_insp':
            EquipNo = request.form.get('o_equip_no')
            Condition = request.form.get('o_condition')

            if not all([EquipNo, Condition]):
                flash('All fields are required.', 'error')
                return redirect(url_for('views.inspection'))

            ConditionPass = conditioncheck(Condition)
            NewInspection = Inspection(equip_no=EquipNo,
                                       condition_code=Condition,
                                       asset_passed=ConditionPass,
                                       user_id=current_user.id)
            db.session.add(NewInspection)
            db.session.commit()
            flash('Inspection has been created.', 'success')
        # processing lifting chain inspections
        if form_id == 'chain_insp':
            EquipNo = request.form.get('equip_no')
            Condition = request.form.get('condition')
            ChainLength = request.form.get('chain_length')
            ChainPitchLength = request.form.get('pitch_length')
            MeasureMeanPitchLength = request.form.get('mean_measured_pitch_length')
            PitchesMeasured = request.form.get('pitches_measured')

            if not all([EquipNo, Condition, ChainLength, ChainPitchLength, MeasureMeanPitchLength, PitchesMeasured]):
                flash('All fields are required.', 'error')
                return redirect(url_for('views.inspection'))

            ConditionPass = conditioncheck(Condition)
            HealthScore = lchealthscore(MeasureMeanPitchLength, ChainPitchLength)
            HealthScorePass = lcpass(ConditionPass, HealthScore)
            NewInspection = Inspection(equip_no=EquipNo,
                                       condition_code=Condition,
                                       chain_length=ChainLength,
                                       chain_pitch_length=ChainPitchLength,
                                       measure_mean_pitch_length=MeasureMeanPitchLength,
                                       pitches_measured=PitchesMeasured,
                                       lc_health_score=HealthScore,
                                       asset_passed=HealthScorePass,
                                       user_id=current_user.id)
            db.session.add(NewInspection)
            db.session.commit()
            flash('Inspection has been created.', 'success')
    LiftingChainList = db.session.query(Asset.equip_no, Asset.description).filter_by(equip_class='C5').all()
    OtherAssetList = db.session.query(Asset.equip_no, Asset.description).filter(Asset.equip_class != 'C5').all()
    ConditionList = db.session.query(ConditionModel).all()
    return render_template('inspection.html', user=current_user, min_length=MIN_CHAIN_LENGTH,
                           max_length=MAX_CHAIN_LENGTH, min_pitch_length=MIN_PITCH_LENGTH,
                           max_pitch_length=MAX_PITCH_LENGTH, min_pitches_measured=MIN_PITCHES_MEASURED,
                           lifting_chain_list=LiftingChainList, condition_list=ConditionList,
                           other_asset_list=OtherAssetList)


@views.route('/inspadmin', methods=['GET', 'POST'])
@admin_required
def inspadmin():
    InspectionList = db.session.query(Inspection.id, Inspection.equip_no, Inspection.condition_code,
                                      Inspection.lc_health_score, Inspection.asset_passed, Inspection.insp_date,
                                      Inspection.user_id, User.first_name, User.surname, User.username).join(User,
                                                                                                             Inspection.user_id == User.id).all()
    return render_template('inspadmin.html', user=current_user, inspections=InspectionList)


@views.route('/inspadmin/<int:id>', methods=['POST'])
@admin_required
def delete_insp(id):
    DeleteInsp = Inspection.query.get(id)
    if DeleteInsp:
        db.session.delete(DeleteInsp)
        db.session.commit()
        flash('Inspection has been deleted.', 'success')
    else:
        flash('Inspection cannot be deleted.', 'error')

    return redirect(url_for('views.inspadmin'))


@views.route('/delete_user/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    DeleteUser = User.query.get(id)
    if DeleteUser:
        db.session.delete(DeleteUser)
        db.session.commit()
        flash('User has been successfully deleted', category='success')
    else:
        flash('Error user not found', category='error')

    return redirect(url_for('auth.useradmin'))


@views.route('/update_role/<int:id>', methods=['POST'])
@admin_required
def update_role(id):
    NewRole = request.form.get('role')
    RolesList = db.session.execute(
        select(Role.role_name)
    ).scalars().all()
    if NewRole not in RolesList:
        flash('Role does not exist', category='error')
    else:
        ChangingUser = User.query.get(id)
        if ChangingUser:
            ChangingUser.user_role = NewRole
            db.session.commit()
            flash('Role has been successfully updated', category='success')
        else:
            flash('User not found', category='error')

    return redirect(url_for('auth.useradmin'))
