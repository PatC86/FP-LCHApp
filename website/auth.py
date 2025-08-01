# Name      : auth
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 02/08/2025
# Purpose   : Define authentication for application

from flask import Blueprint, render_template, request, flash
from flask_login import login_user, logout_user, login_required, current_user

MIN_USERNAME_LENGTH = 5
MIN_FIRST_NAME_LENGTH = 2
MIN_SURNAME_LENGTH = 2
MIN_PASSWORD_LENGTH = 8
PASSWORD_REGEX = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Username = request.form['username']
        Password = request.form['password']


    return render_template('login.html')

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    return "<h1>Logout Page</h1>"

@auth.route('/useradmin', methods=['GET', 'POST'])
def useradmin():
    if request.method == 'POST':
        Username = request.form['username']
        FirstName = request.form['first_name']
        Surname = request.form['surname']
        Role = request.form['role']
        Password1 = request.form['password1']
        Password2 = request.form['password2']

        if len(Username) < MIN_USERNAME_LENGTH:
            flash('Username is less than minimum length of 5', category='error')
        elif len(FirstName) < MIN_FIRST_NAME_LENGTH:
            flash('First name is less than minimum length of 2', category='error')
        elif len(Surname) < MIN_SURNAME_LENGTH:
            flash('Surname is less than minimum length of 2', category='error')
        elif len(Password1) < MIN_PASSWORD_LENGTH:
            flash('Password is less than minimum length of 8', category='error')
        elif Password1 != Password2:
            flash('Passwords do not match', category='error')
        else:
            flash('Account created successfully', category='success')


    return render_template('useradmin.html')
