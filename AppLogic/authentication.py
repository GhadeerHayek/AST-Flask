from config import Config 
from flask import current_app 
from flask import Flask, Blueprint,jsonify, request, make_response
from database import mysql 
import jwt 

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
    # receive inputs 
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    # check inputs from being empty, ensure they're strings, and trim any leading or trailing spaces
    check_username_condition = username and isinstance(username, str) and username.strip()
    check_password_condition = password and isinstance(password, str) and password.strip()
    check_email_condition = email and isinstance(email, str) and email.strip()
    # check all inputs to add to database 
    if username and password and email:
        # TODO: first of all you should check for the uniqness of this data then consider saving
        # save to database and return response 
        query = "INSERT INTO users (name,email,password) VALUES ('{0}','{1}','{2}')".format(username,email,password)
        cursor = mysql.connection.cursor()
        result = cursor.execute(query)
        # all query data are considered as a temporary session data, all are cached and deleted after the session is over
        # so i had to user commit to make the insertion permenant
        mysql.connection.commit()
        cursor.close()
        if result: 
            # success
            return jsonify({"success": "user created", "rows affected:":str(result)})
    else: 
        # return error 
        return jsonify({"error": "invalid output"})


""" 
    This API performs login operation 
        - Input: email, password 
        - Output: authentication token
"""
# TODO
@auth_blueprint.route('/auth/login', methods=['POST'])
def perform_login():
    pass