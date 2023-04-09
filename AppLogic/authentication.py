from config import Config
from flask import current_app
from flask import Flask, Blueprint, jsonify, request, make_response
from database import mysql
import jwt
from AppLogic import token as token_logic 

# routes blueprint
auth_blueprint = Blueprint("auth", __name__)

# this is just a dummy route to check whether database connectivity works just fine.
# also, so we can imagine how database operations will go.

""" 
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
    # check inputs from being empty, ensure they're strings, and trim any leading or trailing spaces
    check_username_condition = username and isinstance(
        username, str) and username.strip()
    check_password_condition = password and isinstance(
        password, str) and password.strip()
    check_email_condition = email and isinstance(email, str) and email.strip()
    # check all inputs to add to database
    if check_username_condition and check_password_condition and check_email_condition:
        u_query = "SELECT email from users where email = %(user_email)s;"
        u_cursor = mysql.connection.cursor()
        u_cursor.execute(u_query, {"user_email":email})
        u_result = u_cursor.fetchone()
        u_cursor.close()
        if u_result:
            return jsonify({"status":"error", "message":"email is duplicated"})
        else:
            i_query = "INSERT INTO users (name, email, password) VALUES (%(user_name)s, %(user_email)s, %(user_password)s);"
            i_cursor = mysql.connection.cursor()
            i_result = i_cursor.execute(i_query, {"user_name": username, "user_email":email, "user_password": password})
            mysql.connection.commit()
            i_cursor.close()
            if i_result:
                return jsonify({"status":"success", "message":"user is created, rows affected: {0}".format(str(i_result))})
            else:
                return jsonify({"status": "failure", "message":"failed to create"})
    else:
        # return error
        return jsonify({"status": "error","message": "invalid input"})

@auth_blueprint.route('/auth/mock', methods=['POST'])
def mock():
     # receive inputs
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    
    query = " SELECT email from users where email = %(user_email)s;"
    cursor = mysql.connection.cursor()
    cursor.execute(query, {"user_email":email})
    result = cursor.fetchone()
    if email == result[0]:
        return jsonify({"message": "duplicated"})
    return jsonify(result)


""" 
    This API performs login operation 
        - Input: email, password 
        - Output: authentication token
"""


@auth_blueprint.route('/auth/login', methods=['POST'])
def perform_login():
    username = request.form['username']
    password = request.form['password']
    # 1- verify the input and its format + escape it.
    # check inputs from being empty, ensure they're strings, and trim any leading or trailing spaces
    check_username_condition = username and isinstance(
        username, str) and username.strip()
    check_password_condition = password and isinstance(
        password, str) and password.strip()
    if check_username_condition and check_password_condition:
        # 2- perform queries on the database to locate the username and the password
        cursor = mysql.connection.cursor()
        # NOTE: .format is know for being not secured and vulnerable to sql injections
        # query = "SELECT * from users where name='{0}' and password='{1}'".format(
        #    username, password)
        # but parameterized query ensures no sql injections by using the %s placeholder to convert whatever you put here to a string 
        query_escape = """ SELECT * from users where name =%(username)s and password= %(password)s """
        cursor.execute(query_escape, {'username':username, "password":password})
        result = cursor.fetchone()
        cursor.close()
        # 3- after query is performed, then you should check whether you got a username and a correct password
        # apparently, the return type is tuple
        # 4- if match is found -> create token based on the user record on the database -> return token
        if result:
            if len(result) > 0:
                token = token_logic.generate_token(result, current_app.config['SECRET_KEY'])
                # prepare response
                response = make_response(jsonify({"status": 200, "message": "token is generated successfully."}))
                response.set_cookie('access_token', token, httponly=True)
                return response
        # 5- if no match, print an apropriate error message.
        else:
            response_text = {'error': 'Invalid credentials, login failed'}
            return jsonify(response_text)
