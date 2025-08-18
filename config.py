# Name      : config
# Author    : Patrick Cronin
# Date      : 19/07/2025
# Updated   : 17/08/2025
# Purpose   : Config settings for application.

from dotenv import load_dotenv
import os


# db and secret key config for application
class Config:
    load_dotenv()
    try:
        SECRET_KEY = os.getenv('SECRET_KEY')
    except KeyError:
        raise EnvironmentError('Please set the SECRET_KEY env variable')
    try:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
        # SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    except Exception as e:
        raise EnvironmentError('Please set the DATABASE_URI env variable')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
