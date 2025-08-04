# Name      : views
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 04/08/2025
# Purpose   : Define views for application

from flask import Blueprint, render_template, flash, url_for
from flask_login import current_user, login_required
from werkzeug.utils import redirect

from . import db
from .userrolewrappers import admin_required

from website.models import Site, Asset, Assetclass, Assetstatus, User

views = Blueprint('views', __name__)


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
                                 Assetclass.class_description, Assetstatus.status_description, Site.description.label('site_desc')).join(
        Assetclass,
        Asset.equip_class == Assetclass.class_id).join(
        Assetstatus, Asset.equip_status == Assetstatus.status_id).join(Site, Asset.site_no == Site.site_no).all()
    print(AssetList)
    return render_template('assets.html', user=current_user, assets=AssetList)

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
