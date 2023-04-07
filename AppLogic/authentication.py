from flask import Flask, Blueprint,jsonify
from database import mysql 
# routes blueprint
auth_blueprint = Blueprint("auth", __name__)

# this is just a dummy route to check whether database connectivity works just fine.
# also, so we can imagine how database operations will go.
@auth_blueprint.route('/database', methods=['GET'])
def index():
    # begin by opening a cursor
    cursor = mysql.connection.cursor()
    # execute query 
    cursor.execute("select * from users")
    # fetch results
    results = cursor.fetchall()
    cursor.close()
    # do whatever you want with the results.
    return jsonify(results)

""" 
    This API performs SignUp operation 
        - Input: username, email, and password.
        - Output: the newly created user id
"""
#TODO
@auth_blueprint.route('/auth/signup', methods=['POST'])
def perform_signup():
    pass 


""" 
    This API performs login operation 
        - Input: email, password 
        - Output: authentication token
"""
# TODO
@auth_blueprint.route('/auth/login', methods=['POST'])
def perform_login():
    pass 