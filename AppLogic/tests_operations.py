"""
    This class concerned with operations that manuiplate tests data, includes read, write and so. 
"""

from flask import Flask, Blueprint,jsonify
from database import mysql 
# routes blueprint
test_op_blueprint = Blueprint("test_op", __name__)

"""
    This API takes test data + authentication token as a parameter. Then, creates a test for the user in the database and returns its id.
    - Input: Bacteria, Sample type, name of the person who created the test 
    - Output: the newly created test id 

"""
@test_op_blueprint.route('/test/create', methods=['POST'])
#TODO
def create_user_test():
    pass 

"""
    This API is concerned with saving user adjustments on antibiotics labels and inhibition zone radius.
    - Input: json string which is a list of antibiotic objects, those objects contain the user adjustment on the original analysis data.
    - Output: test_id
"""
@test_op_blueprint.route('/test/confirmation', methods=['POST'])
#TODO
def save_user_adjustments():
    pass 