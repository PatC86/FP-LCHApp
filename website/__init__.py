# Name      : main
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 02/08/2025
# Purpose   : Initialisation of application.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create flask app using config from config.py
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')


    from .csp import csp
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
