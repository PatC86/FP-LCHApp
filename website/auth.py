# Name      : auth
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 21/07/2025
# Purpose   : Define authentication for application

from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return "<h1>Login Page</h1>"

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    return "<h1>Logout Page</h1>"

@auth.route('/useradmin', methods=['GET', 'POST'])
def useradmin():
    return "<h1>User Admin Page</h1>"

