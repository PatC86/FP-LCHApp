# Name      : config
# Author    : Patrick Cronin
# Date      : 19/07/2025
# Updated   : 20/07/2025
# Purpose   : Db config settings.

# Secret key and database uri hardcoded for project would place in .env file in real world situation.
class Config:
    SECRET_KEY = 'IHAVEASTINKYCAT'
    SQLALCHEMY_DATABASE_URI = 'postgresql://fp_lchproddb_user:IY8HP1nd2RZEDHcRGdoOurUjEtIam7Eh@dpg-d1tqmhk9c44c73cbdjl0-a.frankfurt-postgres.render.com/fp_lchproddb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False