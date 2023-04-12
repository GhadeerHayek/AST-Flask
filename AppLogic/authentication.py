from config import Config
from flask import current_app
from flask import Flask, Blueprint, jsonify, request, make_response
from database import mysql
import jwt
from AppLogic import token as token_logic
from AppLogic import helper  

# routes blueprint
auth_blueprint = Blueprint("auth", __name__)

""" 
    This API performs SignUp operation 
        - Input: username, email, and password.
        - Output: the newly created user id
"""


@auth_blueprint.route('/auth/signup', methods=['POST'])
def perform_signup():
    # receive inputs
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    # check all inputs to add to database
    if helper.validate_string(username) and helper.validate_string(password) and helper.validate_email(email):
        u_query = "SELECT email from users where email = %(user_email)s;"
        u_cursor = mysql.connection.cursor()
        u_cursor.execute(u_query, {"user_email": email})
        u_result = u_cursor.fetchone()
        u_cursor.close()
        if u_result:
            return jsonify({"status": "error", "message": "email is duplicated"})
        else:
            i_query = "INSERT INTO users (name, email, password) VALUES (%(user_name)s, %(user_email)s, %(user_password)s);"
            i_cursor = mysql.connection.cursor()
            i_result = i_cursor.execute(
                i_query, {"user_name": username, "user_email": email, "user_password": password})
            mysql.connection.commit()
            i_cursor.close()
            if i_result:
                return jsonify({"status": "success", "message": "user is created, rows affected: {0}".format(str(i_result))})
            else:
                return jsonify({"status": "failure", "message": "failed to create"})
    else:
        # return error
        return jsonify({"status": "error", "message": "invalid input"})


""" 
    This API performs login operation 
        - Input: email, password 
        - Output: authentication token
"""


@auth_blueprint.route('/auth/login', methods=['POST'])
def perform_login():
    # receive inputs
    username = request.form['username']
    password = request.form['password']
    # check inputs from being empty, ensure they're strings, and trim any leading or trailing spaces
    u = helper.validate_string(username)
    p = helper.validate_string(password)
    if u and p:
        # check for credentials
        cursor = mysql.connection.cursor()
        query = " SELECT * from users where name =%(username)s and password= %(password)s "
        cursor.execute(
            query, {'username': username, "password": password})
        result = cursor.fetchone()
        cursor.close()
        if result:
            if len(result) > 0:
                token = token_logic.generate_token(
                    result, current_app.config['SECRET_KEY'])
                # prepare response
                response = make_response(
                    jsonify({"status": "success", "message": "token is generated successfully."}))
                response.set_cookie('access_token', token, httponly=True)
                return response
        # no match credentials
        else:
            return jsonify({"status": "error", "message": "Invalid credentials, login failed"})
    else:
        return jsonify({"status":"failure", "message":"invalid input", "u":u , "p":p})