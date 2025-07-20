# Name      : views
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 20/07/2025
# Purpose   : Define views for application

from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "<h1>HELLO KITTY CAT</H1>"

