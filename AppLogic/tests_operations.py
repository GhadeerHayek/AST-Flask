"""
    This class concerned with operations that manuiplate tests data, includes read, write and so. 
"""

from flask import Flask, Blueprint, jsonify, request, current_app
from database import mysql
from werkzeug.utils import secure_filename
from datetime import datetime
from AppLogic.token import authorize_user
from AppLogic import helper
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
        return jsonify({"Status": "Failure", "Message": "No file provided"})
    if 'bacteria' not in request.form:
        return jsonify({"Status": "Failure", "Message": "No bacteria input provided"})
    if 'sample_type' not in request.form:
        return jsonify({"Status": "Failure", "Message": "No sample type input provided"})
    if 'access_token' not in request.cookies:
        return jsonify({"Status": "Failure", "Message": "invalid request, no token"})
    file = request.files['file']
    bacteria = request.form['bacteria']
    sample_type = request.form['sample_type']
    token = request.cookies['access_token']
    payload = authorize_user(token)
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
            return jsonify({"Status": "Failure", "Message": "Insertion failed"})
        mysql.connection.commit()
        cursor.close()
        return jsonify({"Status": "Sucess", "Message": "Insertion was successful", "test_id": str(test_id)})
    else:
        return jsonify({"Status": "Failure", "Message": "Invalid input"})


"""
    This API is concerned with saving user adjustments on antibiotics labels and inhibition zone radius.
    - Input: json string which is a list of antibiotic objects, those objects contain the user adjustment on the original analysis data.
    - Output: test_id
"""


@test_op_blueprint.route('/test/confirmation', methods=['POST'])
def save_user_adjustments():
    if 'access_token' not in request.cookies:
        return jsonify({"Status": "Failure", "Message": "Invalid request, no token"})
    if 'test_id' not in request.form:
        return jsonify({"Status": "Failure", "Message": "Invalid request, no test_id"})
    if 'image_info' not in request.form:
        return jsonify({"Status": "Failure", "Message": "Invalid request, no data"})
    token = request.cookies['access_token']
    try:
        test_id = int(request.form['test_id'])
        json_response = request.form['image_info']
        payload = authorize_user(token)
        if not payload:
            return jsonify({"Status": "Failure", "Message": "Invalid token"})
        # validate test_id
        test_query = "SELECT * from tests where id = %(test_id)s"
        test_cursor = mysql.connection.cursor()
        test_cursor.execute(test_query, {"test_id": test_id})
        test_result = test_cursor.fetchone()
        test_cursor.close()
        if not test_result:
            return jsonify({"Status": "Failure", "Message": "No test with this id"})
        else:
            update_data_query = "UPDATE tests SET user_adjustments = %(data)s WHERE id = %(test_id)s"
            update_cursor = mysql.connection.cursor()
            rows_affected = update_cursor.execute(
                update_data_query, {"data": json_response, "test_id": test_id})
            mysql.connection.commit()
            update_cursor.close()
            if rows_affected is None:
                return jsonify({"Status": "Failure", "Message": "failed to update the values"})
            else:
                return jsonify({"Status": "Success", "Message": "successfully updated the test, rows affected: {0}".format(rows_affected)})
    except ValueError:
        return jsonify({"Status": "Failure", "Message": "Test ID format is not recognized"})
