"""
    This class concerned with operations that manuiplate tests data, includes read, write and so. 
"""

from flask import Flask, Blueprint,jsonify, request, current_app
from database import mysql 
from werkzeug.utils import secure_filename
from datetime import datetime
from AppLogic import helper  
from AppLogic.validate_token import check_token_validity
import os



# routes blueprint
test_op_blueprint = Blueprint("test_op", __name__)

"""
    This API takes test data + authentication token as a parameter. Then, creates a test for the user in the database and returns its id.
    - Input: Bacteria, Sample type, name of the person who created the test 
    - Output: the newly created test id 

"""
@test_op_blueprint.route('/test/create', methods=['POST'])
def create_user_test():
    if 'file' not in request.files:
        # file not in create test request, reject it 
        return jsonify({"status":"failure", "message":"No file provided"})
    if 'bacteria' not in request.form:
        # don't proceed
        return jsonify({"status":"failure", "message":"No bacteria input provided"}) 
    if 'sample_type' not in request.form:
        # reject 
        return jsonify({"status":"failure", "message":"No sample type input provided"})  
    if 'access_token' not in request.cookies:
        #reject 
        return jsonify({"status":"failure", "message":"invalid request, no token"})  
    file = request.files['file']
    bacteria = request.form['bacteria']
    sample_type = request.form['sample_type']
    token = request.cookies['access_token']
    user_id = check_token_validity(token)['id']
    if helper.validate_file(file) and helper.validate_string(bacteria) and helper.validate_string(sample_type):
        filename = secure_filename(file.filename)
        # file is saved in the upload folder
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        # prepare insert query 
        query = "INSERT INTO tests (user_id, sample_type, bacteria, created_at, img) VALUES (%(user_id)s,%(sample_type)s,%(bacteria)s,%(created_at)s,%(img)s)"
        cursor = mysql.connection.cursor()
        cursor.execute(query, {"user_id": user_id, "sample_type":sample_type, "bacteria":bacteria, "created_at":datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S'), "img":img_path })
        test_id = cursor.lastrowid
        if test_id is None:
            # return failure
            return jsonify({"status":"failure", "message":"Insertion failed"}) 
        mysql.connection.commit()
        cursor.close()
        # return success message and test_id 
        return jsonify({"status":"sucess", "message":"Insertion was successful", "test_id":str(test_id)}) 
    else:
        return jsonify({"status":"failure", "message":"input format not valid"})

"""
    This API is concerned with saving user adjustments on antibiotics labels and inhibition zone radius.
    - Input: json string which is a list of antibiotic objects, those objects contain the user adjustment on the original analysis data.
    - Output: test_id
"""
@test_op_blueprint.route('/test/confirmation', methods=['POST'])
#TODO
def save_user_adjustments():
    pass 