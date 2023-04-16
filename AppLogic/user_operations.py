"""
    This class concerned with operations that manuiplate user's data, includes read, write and so. 
"""

from flask import Flask, Blueprint,jsonify, current_app, request
from database import mysql 
import jwt
from AppLogic.token import authorize_user
# routes blueprint
user_op_blueprint = Blueprint("user_op", __name__)


"""
    This is an API that gets all users tests based on a token that is sent in user's request 
    - Input: authentication token 
    - Output: list of tests that were performed by this user 
"""
@user_op_blueprint.route('/user/tests', methods=['GET'])
def get_user_tests():
    # check if the access token exists
    if "access_token" not in request.cookies:
        return jsonify({"Status":"Failure", "Message": "Missing token"})
    # get payload(user's data) from the token 
    token = request.cookies['access_token']
    payload = authorize_user(token)
    if not payload:
        return jsonify({"Status":"Error", "Message":"Token not valid"})
    # get user id from the token 
    user_id = payload["id"]
    cursor = mysql.connection.cursor()
    # get all user's test based on his/her id
    query = """SELECT * from tests where user_id = %(user_id)s"""
    cursor.execute(query, {"user_id":user_id})
    results = cursor.fetchall()
    if results is None :
        return jsonify({"Tests_count": results_count, "data": []})   
        # return jsonify({"status":"error", "message":"no tests found"})
    results_count = len(results)
    # Convert result to list of dictionaries
    columns = [column[0] for column in cursor.description]
    result_dict = [dict(zip(columns, row)) for row in results]
    return jsonify({"tests_count": results_count, "data": result_dict})                       
    
