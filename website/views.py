# Name      : views
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 20/07/2025
# Purpose   : Define views for application

from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')
