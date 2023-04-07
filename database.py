"""
    Database connection configuration and initialization.
"""
from flask_mysqldb import MySQL 

mysql = MySQL()

def init_app(app):
    # database configurations are in config file
    # initializes the app 
    mysql.init_app(app)