# Name      : config
# Author    : Patrick Cronin
# Date      : 19/07/2025
# Updated   : 02/08/2025
# Purpose   : Config settings for application.

from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    #SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    #SQLALCHEMY_TRACK_MODIFICATIONS = False