# Name      : config
# Author    : Patrick Cronin
# Date      : 19/07/2025
# Updated   : 20/07/2025
# Purpose   : Db config settings.

from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    secret_key = os.getenv('SECRET_KEY')
    sqlalchemy_database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False