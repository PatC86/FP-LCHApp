# Name      : auth
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 01/08/2025
# Purpose   : Define authentication for application

from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    return "<h1>Logout Page</h1>"

@auth.route('/useradmin', methods=['GET', 'POST'])
def useradmin():
    return render_template('useradmin.html')
