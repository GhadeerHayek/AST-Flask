from config import Config
from flask import Flask, Blueprint, jsonify, request, make_response, current_app
from database import mysql
import jwt
from AppLogic import token as token_logic, helper
from werkzeug.security import generate_password_hash, check_password_hash
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
    # check all inputs then add to database
    if helper.validate_string(username) and helper.validate_string(password) and helper.validate_email(email):
        # check if email is unique
        u_query = "SELECT email from users where email = %(user_email)s;"
        u_cursor = mysql.connection.cursor()
        u_cursor.execute(u_query, {"user_email": email})
        u_result = u_cursor.fetchone()
        u_cursor.close()
        # email is unique,  insert
        if u_result is None:
            hashed_pass = generate_password_hash(password, "sha256")
            i_query = "INSERT INTO users (name, email, password) VALUES (%(user_name)s, %(user_email)s, %(user_password)s);"
            i_cursor = mysql.connection.cursor()
            i_result = i_cursor.execute(
                i_query, {"user_name": username, "user_email": email, "user_password": hashed_pass})
            mysql.connection.commit()
            i_cursor.close()
            # insertion success
            if i_result:
                return jsonify({"Status": "Success", "Message": "User is created, rows affected: {0}".format(str(i_result))})
            # insertion failure
            else:
                return jsonify({"Status": "Failure", "Message": "Failed to create"})
        # email is duplicated, no insertion
        else:
            return jsonify({"Status": "Failure", "Message": "Email is duplicated"})
    # input format not valid
    else:
        return jsonify({"Status": "Failure", "Message": "Invalid input"})


""" 
    This API performs login operation 
        - Input: email, password 
        - Output: authentication token in response cookies/headers
"""


@auth_blueprint.route('/auth/login', methods=['POST'])
def perform_login():
    # receive inputs
    email = request.form['email']
    password = request.form['password']
    # check inputs
    if helper.validate_email(email) and helper.validate_string(password):
        # check for credentials
        cursor = mysql.connection.cursor()
        query = " SELECT * from users where email =%(email)s"
        cursor.execute(
            query, {'email': email})
        result = cursor.fetchone()
        # no match, no user
        if result is None:
            return jsonify({"Status": "Failure", "Message": "Incorrect username or password "}) 
        correct_pass = check_password_hash(result[3], password)
        cursor.close()
        if correct_pass is False:
            return jsonify({"Status": "Failure", "Message": "Incorrect username or password "}) 
        token = token_logic.generate_token(
            result, current_app.config['SECRET_KEY'])
        # prepare response
        response = make_response(
            jsonify({"Status": "Success", "Message": "token is generated successfully."}))
        response.set_cookie('access_token', token, httponly=True)
        return response
    else:
        return jsonify({"Status": "Failure", "Message": "invalid input"})
