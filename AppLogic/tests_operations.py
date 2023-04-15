"""
    This class concerned with operations that manuiplate tests data, includes read, write and so. 
"""

from flask import Flask, Blueprint, jsonify, request, current_app
from database import mysql
from werkzeug.utils import secure_filename
from datetime import datetime
from AppLogic.token import check_token_validity
import os
from AppLogic import helper


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
        return jsonify({"status": "failure", "message": "No file provided"})
    if 'bacteria' not in request.form:
        return jsonify({"status": "failure", "message": "No bacteria input provided"})
    if 'sample_type' not in request.form:
        return jsonify({"status": "failure", "message": "No sample type input provided"})
    if 'access_token' not in request.cookies:
        return jsonify({"status": "failure", "message": "invalid request, no token"})
    file = request.files['file']
    bacteria = request.form['bacteria']
    sample_type = request.form['sample_type']
    token = request.cookies['access_token']
    payload = check_token_validity(token)
    if payload and helper.validate_file(file) and helper.validate_string(bacteria) and helper.validate_string(sample_type):
        user_id = payload["id"]
        filename = secure_filename(file.filename)
        img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(img_path)
        # prepare insert query
        query = "INSERT INTO tests (user_id, sample_type, bacteria, created_at, img) VALUES (%(user_id)s,%(sample_type)s,%(bacteria)s,%(created_at)s,%(img)s)"
        cursor = mysql.connection.cursor()
        cursor.execute(query, {"user_id": user_id, "sample_type": sample_type, "bacteria": bacteria,
                       "created_at": datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S'), "img": img_path})
        test_id = cursor.lastrowid
        if test_id is None:
            return jsonify({"status": "failure", "message": "Insertion failed"})
        mysql.connection.commit()
        cursor.close()
        return jsonify({"status": "sucess", "message": "Insertion was successful", "test_id": str(test_id)})
    else:
        return jsonify({"status": "failure", "message": "input format not valid"})


"""
    This API is concerned with saving user adjustments on antibiotics labels and inhibition zone radius.
    - Input: json string which is a list of antibiotic objects, those objects contain the user adjustment on the original analysis data.
    - Output: test_id
"""


@test_op_blueprint.route('/test/confirmation', methods=['POST'])
# TODO
def save_user_adjustments():
    if 'access_token' not in request.cookies:
        return jsonify({"status": "failure", "message": "invalid request, no token"})
    if 'test_id' not in request.form:
        return jsonify({"status": "failure", "message": "invalid request, no test_id"})
    if 'image_info' not in request.form:
        return jsonify({"status": "failure", "message": "invalid request, no data"})
    token = request.cookies['access_token']
    test_id = int(request.form['test_id'])
    json_response = request.form['image_info']
    payload = check_token_validity(token)
    if not payload:
        return jsonify({"status":"failure", "message":"invalid token"})
    # validate test_id
    test_query = "SELECT * from tests where id = %(test_id)s"
    test_cursor = mysql.connection.cursor()
    test_cursor.execute(test_query, {"test_id":test_id})
    test_result = test_cursor.fetchone()
    test_cursor.close()
    if not test_result:
        return jsonify({"status":"failure", "message":"no test with this id"})
    else:
        # NOTE: parameterized query that insertes strings and integers at the same time is not working, i couldn't
        # find a proper solution for it, so i am just gonna give up and stick to .format
        # update_data_query = "UPDATE tests SET user_adjustments = %(data)s WHERE id = %(test_id)s"
        update_data_query = "UPDATE tests SET user_adjustments = '{0}' WHERE id = {1}".format(json_response, test_id)
        update_cursor = mysql.connection.cursor()
        #update_cursor.execute(update_data_query, { "data": json_response,"test_id": test_id})
        rows_affected = update_cursor.execute(update_data_query)
        mysql.connection.commit()
        update_cursor.close()   
        if rows_affected is None:
            return jsonify({"status": "failure", "message": "failed to update the values"})
        else:
            return jsonify({"status": "success", "message": "successfully updated the test, rows affected: {0}".format(rows_affected)})