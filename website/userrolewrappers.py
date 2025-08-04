# Name      : userrolewrappers
# Author    : Patrick Cronin
# Date      : 01/08/2025
# Updated   : 04/08/2025
# Purpose   : Define wrappers for different user roles

import logging
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user, login_required


def admin_required(f):
    """Wrapper to ensure that the user is logged in with admin role. To restrict access for certain functions and views"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        try:
            if not current_user.user_role.upper() == 'ADMIN':
                flash('You must be an administrator.', category='error')
                abort(403)
        except AttributeError as e:
            logging.error(f"Error checking role: {e}")
            flash('An error has occurred. Please retry', category='error')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logging.error(f"Error checking role: {e}")
            flash('An error has occurred. Please retry', category='error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def contractmanager_required(f):
    """Wrapper to ensure that user is logged in with contract manager role. To restrict access for certain functions and views"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        try:
            if not current_user.user_role.upper() == 'CONTENG':
                flash('You must be an contract manager.', category='error')
                abort(403)
        except AttributeError as e:
            logging.error(f"Error checking role: {e}")
            flash('An error has occurred. Please retry', category='error')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logging.error(f"Error checking role: {e}")
            flash('An error has occurred. Please retry', category='error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function

