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
    username = request.form['username']
    password = request.form['password']
    # 1- verify the input and its format + escape it. 
    # check inputs from being empty, ensure they're strings, and trim any leading or trailing spaces
    check_username_condition = username and isinstance(username, str) and username.strip()
    check_password_condition = password and isinstance(password, str) and password.strip()
    if check_username_condition and check_password_condition:
        # 2- perform queries on the database to locate the username and the password 
        # NOTE: those are dummy inputs for test purposes only, they are replaced with db queries. 
        # dummy_username = "Ghadeer"
        # dummy_password = "ghadeer123"
        cursor = mysql.connection.cursor()
        query = "SELECT * from users where name='{0}' and password='{1}'".format(username, password)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        # 3- after query is performed, then you should check whether you got a username and a correct password 
        # apparently, the return type is tuple 
        # 4- if match is found -> create token based on the user record on the database -> return token 
        if len(result) > 0:
            # a match is found
            # generate token
            token_payload ={
                "id": result[0],
                "name": result[1],
                "email": result[2],
                "password": result[3]
            }
            token = jwt.encode(token_payload,current_app.config['SECRET_KEY'], algorithm='HS256')
            # prepare response 
            response = make_response(jsonify(token_payload))
            response.set_cookie('access_token', token, httponly=True)
            return response
        # 5- if no match, print an apropriate error message. 
        else:
            response_text = {'error': 'Invalid credentials, login failed'}
            return jsonify(response_text)