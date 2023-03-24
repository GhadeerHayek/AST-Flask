"""
    This file is only concerned with database operations.
"""

from flask_mysqldb import MySQL
from app import app 

def get_mysql():
    # Create a database connection
    app.config['MYSQL_HOST'] =  '192.168.0.104'
    app.config['MYSQL_USER'] = 'WSL_USER'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'flask_db_test'
    mysql = MySQL(app)
    return mysql

def get_cursor():
    # Create a cursor object
    mysql = get_mysql()
    cursor = mysql.connection.cursor()
    return cursor

def close_cursor(cursor):
    # Close the cursor object
    cursor.close() 