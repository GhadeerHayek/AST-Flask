import os, astimp, jwt
from flask import Flask, flash, request, redirect, send_file, Blueprint, current_app, jsonify
from app import app
from werkzeug.utils import secure_filename
from AppLogic import AST as AST
from AppLogic.token import verify_token
from AppLogic.validate_token import check_token_validity
from database import mysql

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

crop_blueprint = Blueprint("crop", __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""
    This route indicates an API endpoint, it recieves an image through post request. 
    The image is analyzed, its ROIs are extracted, cropped and saved to crop directory.
    TODO: verify data types in db
"""


@crop_blueprint.route('/process/crops', methods=['POST'])
def analyze_image_crops():
    payload = check_token_validity(request.cookies["access_token"])
    user_id = payload["id"]
    cursor = mysql.connection.cursor()
    # prepare return data
    # filename will be fetched according to the "test_id"
    test_id = request.form['test_id']
    test_id_query = "SELECT img FROM tests where id=%(test_id)s"
    cursor.execute(test_id_query, {'test_id':test_id})
    # to fetch the id as a string returned from the query
    parent_dir_filename = cursor.fetchone()[0]
    # then use the filename
    num_of_crops, data = AST.process_image_to_crops(parent_dir_filename)
    # prepare sql statement
    query = """INSERT INTO cropped_antibiotics 
    (test_id, img_name, label, path, parent_directory, centerX, centerY, width, height, inhibition_radius) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    result = ""
    atb_ids = []
    # inside a (try catch) to ensure (result) is always executed right
    try : 
        # loop through each antibiotic to insert it to db  
        for atb in data:
            atb_data = {}
            values = (test_id, atb["img_name"], atb["label"], atb["img_folder"], parent_dir_filename, atb["centerX"], atb["centerY"], atb["width"], atb["height"], atb["inhibition_radius"])
            result = cursor.execute(query, values)
            atb_data['img_id'] = cursor.lastrowid
            atb_ids.append(atb_data)
    except Exception as e: 
        mysql.connection.rollback()
        return jsonify({'error': str(e)})
    # user commit to make the insertion permenant
    mysql.connection.commit()
    cursor.close()
    if result:
        # success -> return atb ids 
        return jsonify({"num of crops":len(atb_ids)}, atb_ids)
    


"""
     This route indicates an API endpoint, which recieves a request containing an image name and its path,
      then returns the image with this specific information,
"""


@crop_blueprint.route('/fetch/crop', methods=['POST'])
def get_crop():
    payload = check_token_validity(request.cookies["access_token"])
    # get user id for later usage
    user_id = payload["id"]
    # if image name and its path not in the request -> don't procceed.
    if 'img_id' not in request.form:
        return "No image is provided!"
    # fetch image name and path from the request
    img_id = request.form['img_id']
    # img_path = request.form['img_path']
    # if the image name or its path are empty -> don't procceed.
    if img_id == '':
        # img_name is dummy -> not acceptable
        return "Blank/empty images are not acceptable!"
    # but if it exists and its extension is allowed
    if img_id:
        # # fetch the image specified, and send it.
        # img = os.path.join(img_path, img_name)
        # return send_file(img)
        cursor = mysql.connection.cursor()
        query = "SELECT img_path, img_name FROM cropped_antibiotics WHERE id=%(img_id)s"
        cursor.execute(query, {'img_id' : img_id})
        result = cursor.fetchone()
        img_path, img_name = result
        cursor.close()
        if result:
            if len(result) > 0:
                img = os.path.join(img_path, img_name)
        else:
            return jsonify({"status": "error", "message": "Invalid credentials, login failed"})

@crop_blueprint.route('/')
def mock_route():
    return "Hello World?"
