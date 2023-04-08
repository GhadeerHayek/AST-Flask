"""
    This class concerned with operations that manuiplate user's data, includes read, write and so. 
"""

from flask import Flask, Blueprint,jsonify, current_app, request
from database import mysql 
import jwt
# routes blueprint
user_op_blueprint = Blueprint("user_op", __name__)


"""
    This is an API that gets all users tests based on a token that is sent in user's request 
    - Input: authentication token 
    - Output: list of tests that were performed by this user 
"""
# TODO
@user_op_blueprint.route('/user/tests', methods=['GET'])
def get_user_tests():
    # our get request now must have a token, this token must be decoded so that we can read the data inside it and use it in our operation.
    # we need the token to authorize the app to display user data. 
    token = request.cookies["access_token"]
    if not token:
        return jsonify({"error": "missing token"})
    payload = authorize_user(token, current_app.config['SECRET_KEY'])
    if payload != "invalid token":
        user_id = payload["id"]
        cursor = mysql.connection.cursor()
        query = "SELECT * from tests where user_id = {0}".format(user_id)
        cursor.execute(query)
        results = cursor.fetchall()
        results_count = len(results)
        if results_count > 0:
            # Convert result to list of dictionaries
            columns = [column[0] for column in cursor.description]
            result_dict = [dict(zip(columns, row)) for row in results]
            return jsonify({"tests_count": results_count, "data": result_dict})
        else:
            return jsonify({"tests_count": results_count, "data": []})
    else:
        return jsonify({"error": payload})
    
