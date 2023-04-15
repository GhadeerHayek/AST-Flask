"""
    This class concerned with operations that manuiplate user's data, includes read, write and so. 
"""

from flask import Flask, Blueprint,jsonify, current_app, request
from database import mysql 
import jwt
from AppLogic.token import check_token_validity
# routes blueprint
user_op_blueprint = Blueprint("user_op", __name__)


"""
    This is an API that gets all users tests based on a token that is sent in user's request 
    - Input: authentication token 
    - Output: list of tests that were performed by this user 
"""
@user_op_blueprint.route('/user/tests', methods=['GET'])
def get_user_tests():
    if "access_token" not in request.cookies:
        return jsonify({"status":"failure", "message": "missing token"})
    token = request.cookies['access_token']
    payload = check_token_validity(token)
    if payload:
        user_id = payload["id"]
        cursor = mysql.connection.cursor()
        query = """SELECT * from tests where user_id = %(user_id)s"""
        cursor.execute(query, {"user_id":user_id})
        results = cursor.fetchall()
        if results is None :
            return jsonify({"tests_count": results_count, "data": []})   
            # return jsonify({"status":"error", "message":"no tests found"})
        else:
            results_count = len(results)
            # Convert result to list of dictionaries
            columns = [column[0] for column in cursor.description]
            result_dict = [dict(zip(columns, row)) for row in results]
            return jsonify({"tests_count": results_count, "data": result_dict})                       
    else:
        return jsonify({"status":"error", "message":"token not valid"})
    
