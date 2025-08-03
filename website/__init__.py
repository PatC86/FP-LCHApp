# Name      : main
# Author    : Patrick Cronin
# Date      : 20/07/2025
# Updated   : 03/08/2025
# Purpose   : Initialisation of application.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()

# Create flask app using config from config.py
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)


    from .csp import csp
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Role

    with app.app_context():
        db.create_all()

    return app

def create_db():
    if not path.exists('database.db'):
        db.create_all()
