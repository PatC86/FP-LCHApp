# Name      : auth
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 17/08/2025
# Purpose   : Define authentication for application

from flask import Blueprint, render_template, request, flash, url_for
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Role
from . import db
from .userrolewrappers import admin_required
import logging

MIN_USERNAME_LENGTH = 5
MIN_FIRST_NAME_LENGTH = 2
MIN_SURNAME_LENGTH = 2
MIN_PASSWORD_LENGTH = 8
PASSWORD_REGEX = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

auth = Blueprint('auth', __name__)


# blueprint route for logging in to web application
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Username = request.form['username']
        Password = request.form['password']

        try:
            user = User.query.filter_by(username=Username).first()
        except Exception as e:
            logging.error(f'Error getting user: {e}')
            flash('Login currently unavailable, try again later.', category='error')
            return redirect(url_for('auth.login'))

        if user:
            try:
                if check_password_hash(user.password, Password):
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect Password', category='error')
                    return redirect(url_for('auth.login'))
            except Exception as e:
                logging.error(f'Error getting user: {e}')
                flash('Login Failed, try again later', category='error')
        else:
            flash('Incorrect Username', category='error')

    return render_template('login.html', user=current_user)


# blueprint route for logging out of web application
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    try:
        logout_user()
    except Exception as e:
        logging.error(f'Error logging user out: {e}')
        flash('Logout failed, please close your browser', category='error')

    return redirect(url_for('auth.login'))


# blueprint route for user admin. Adding and removing user, and changing user roles.
@auth.route('/useradmin', methods=['GET', 'POST'])
@admin_required
def useradmin():
    if request.method == 'POST':
        Username = request.form['username']
        try:
            FirstName = request.form['first_name']
            Surname = request.form['surname']
            UserRole = request.form['role']
            Password1 = request.form['password1']
            Password2 = request.form['password2']

            user = User.query.filter_by(username=Username).first()
            if user:
                flash('Account already created!', category='error')
            elif len(Username) < MIN_USERNAME_LENGTH:
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
                new_user = User(username=Username, first_name=FirstName, surname=Surname, user_role=UserRole,
                                password=generate_password_hash(Password1, method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully', category='success')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error creating and validating user data: {e}')
            flash('Error creating and validating user data', category='error')
    try:
        UserList = db.session.query(User.id, User.username, User.first_name, User.surname, User.user_role,
                                    Role.role_description).join(Role, User.user_role == Role.role_name).all()
        RoleList = db.session.query(Role.role_name, Role.role_description).all()
    except Exception as e:
        logging.error(f'Error getting user and role lists: {e}')
        flash('Error getting user and role lists', category='error')
        UserList, RoleList = [], []

    return render_template('useradmin.html', user=current_user, user_list=UserList, role_list=RoleList)
