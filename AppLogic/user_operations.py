"""
    This class concerned with operations that manuiplate user's data, includes read, write and so. 
"""

from flask import Flask, Blueprint,jsonify
from database import mysql 
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
    pass 
