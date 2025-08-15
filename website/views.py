# Name      : views
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 15/08/2025
# Purpose   : Define views for application

from flask import Blueprint, render_template, flash, url_for, request
from flask_login import current_user, login_required
from werkzeug.utils import redirect
from sqlalchemy import select

from . import db
from .userrolewrappers import admin_required
from .inspections import conditioncheck

from website.models import Site, Asset, Assetclass, Assetstatus, User, Role, Inspection

views = Blueprint('views', __name__)

# flask blueprint view for home page
@views.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)


@views.route('faqs')
def faqs():
    return render_template('faqs.html', user=current_user)


@views.route('/sites')
@login_required
def sites():
    SiteList = db.session.query(Site).all()
    return render_template('sites.html', user=current_user, sites=SiteList)


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

@views.route('/inspection', methods=['GET', 'POST'])
@login_required
def inspection():
    if request.method == 'POST':
        form_id = request.form.get('form')
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

    return render_template('inspection.html', user=current_user)

@views.route('/inspadmin', methods=['GET', 'POST'])
@admin_required
def inspadmin():
    return render_template('inspadmin.html', user=current_user)

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
