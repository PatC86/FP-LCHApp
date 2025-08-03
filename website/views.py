# Name      : views
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 03/08/2025
# Purpose   : Define views for application

from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html', user=current_user)

@views.route('faqs')
def faqs():
    return render_template('faqs.html', user=current_user)
