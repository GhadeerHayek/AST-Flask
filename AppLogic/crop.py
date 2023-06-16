import os
import astimp
import jwt
from flask import Flask, flash, request, redirect, send_file, Blueprint, current_app, jsonify
from werkzeug.utils import secure_filename
from AppLogic import AST as AST
from AppLogic.token import authorize_user
from database import mysql

crop_blueprint = Blueprint("crop", __name__)


"""
    This route indicates an API endpoint, that recieves a test id through a post request. 
    The test id coresponds to an img, which gets analyzed, cropped and saved to the crop directory and the database.
    - Input: test_id 
    - Output: list of img ids that were cropped
"""


@crop_blueprint.route('/process/crops', methods=['POST'])
def analyze_image_crops():
    # check if the access token exists
    if 'access_token' not in request.cookies:
        return jsonify({"Status": "Failure", "Message": "Invalid request, no token"})
    # get payload(user's data) from the token
    token = request.cookies['access_token']
    payload = authorize_user(token)
    if not payload:
        return jsonify({"Status": "Failure", "Message": "empty token, no payload data"})
    try:
        # converting test_id from string to int is an operation that may throw a ValueError Exception
        test_id = int(request.form['test_id'])
        # check if test_id exists
        test_id_query = """SELECT * from tests where id = %(test_id)s;"""
        cursor = mysql.connection.cursor()
        cursor.execute(test_id_query, {"test_id": test_id})
        result = cursor.fetchone()
        # no test_id is found then it's not valid
        if result is None:
            return jsonify({"Status": "Failure", "Message": "No test with this id is found"})
        # fetch the img path
        parent_dir_filename = result[5]
        # then use the filename
        num_of_crops, data = AST.process_image_to_crops(parent_dir_filename)
        # prepare sql statement
        query = """INSERT INTO cropped_antibiotics (test_id, img_name, label, path, parent_directory, centerX, centerY, width, height, inhibition_radius) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        # to track all inserted ids and return them
        atb_ids = []
        # inside a (try catch) to ensure all queries are executed (result) is always executed right
        try:
            # loop through each antibiotic to insert it to db
            for atb in data:
                values = (test_id, atb["img_name"], atb["label"], atb["img_folder"], parent_dir_filename,
                          atb["centerX"], atb["centerY"], atb["width"], atb["height"], atb["inhibition_radius"])
                cursor.execute(query, values)
                # get the id of the inserted img crop and append it to the list
                atb_ids.append(cursor.lastrowid)
        except Exception as e:
            # if any error occurs, rollback db execution
            mysql.connection.rollback()
            return jsonify({"Status": "Failure", "Message": str(e)})
        # to ensure data intergrity,
        # we'll commit only if the length of the (atb_ids) list equals the length of (data) that was generated by (process_image_to_crops)
        if len(atb_ids) == len(data):
            # success -> return atb ids
            mysql.connection.commit()
            cursor.close()
            return jsonify({"Num of crops": len(atb_ids)}, atb_ids)
    except ValueError:
        return jsonify({"Status": "Failure", "Message": "Test ID format is not recognized"})


"""
    This route indicates an API endpoint, which recieves a request containing an cropped image id,
    then returns the image with it details,
    - Input: img_id 
    - Output: the cropped image and its details
"""


@crop_blueprint.route('/fetch/crop', methods=['POST'])
def get_crop():
    # check if the access token exists
    if 'access_token' not in request.cookies:
        return jsonify({"Status": "Failure", "Message": "Invalid request, no token"})
    # get payload(user's data) from the token
    token = request.cookies['access_token']
    payload = authorize_user(token)
    if not payload:
        return jsonify({"Status": "Failure", "Message": "User not authorized"})
    # if image id is not in the request -> don't procceed.
    if 'img_id' not in request.form:
        return jsonify({"Status": "Failure", "Message": "No id is provided!"})
    # fetch image id from the request
    img_id = request.form['img_id']
    cursor = mysql.connection.cursor()
    # get all the image's data
    query = """SELECT * FROM cropped_antibiotics WHERE id=%(img_id)s"""
    # execute the query and pass the named placeholder
    cursor.execute(query, {'img_id': img_id})
    # fetch the result
    resultAll = cursor.fetchone()
    # check if the query returned a result(i.e. it's not None, which means it's true)
    if resultAll is None:
        return jsonify({"Status": "Error", "Message": "The image id you provided doesn't match any stored image id"})
    # get the image path and name to send it to the user
    img_path = resultAll[4]
    img_name = resultAll[2]
    # create an object to store all the image's details
    atb = {}
    # get image's data from the result
    atb['img_id'] = resultAll[0]
    atb['test_id'] = resultAll[1]
    atb['label'] = resultAll[3]
    atb['inhibition_radius'] = resultAll[10]
    atb['centerX'] = resultAll[6]
    atb['centerY'] = resultAll[7]
    atb['width'] = resultAll[8]
    atb['height'] = resultAll[9]
    # join the image name and path to correctly locate the image in the file system and display it
    img = os.path.join(img_path, img_name)
    # send the image along with the response and display it
    response = send_file(img)
    # add the atb object to the response headers as a custom (atb-data) header
    response.headers['atb-data'] = atb
    return response

@crop_blueprint.route('/fetch/draw', methods=['POST'])
def get_petri_dish():
    # check if the access token exists
    if 'access_token' not in request.cookies:
        return jsonify({"Status": "Failure", "Message": "Invalid request, no token"})
    # get payload(user's data) from the token
    token = request.cookies['access_token']
    payload = authorize_user(token)
    if not payload:
        return jsonify({"Status": "Failure", "Message": "User not authorized"})
    # if test id is not in the request -> don't procceed.
    if 'test_id' not in request.form:
        return jsonify({"Status": "Failure", "Message": "No test id is provided!"})
    # fetch image id from the request
    test_id = request.form['test_id']
    cursor = mysql.connection.cursor()
    # get all the image's data
    query = """SELECT * FROM tests WHERE id=%(test_id)s"""
    # execute the query and pass the named placeholder
    cursor.execute(query, {'test_id': test_id})
    print("**************************8")
    print(test_id)
    # fetch the result
    resultAll = cursor.fetchone()
    # check if the query returned a result(i.e. it's not None, which means it's true)
    if resultAll is None:
        return jsonify({"Status": "Error", "Message": "The test id you provided doesn't match any stored test id"})
    # if the dish has already been drawn and proccessed -> just fetch the image 
    processed_image	= resultAll[7]
    if processed_image:
        # send the image 
        response = send_file(processed_image)
        return response 
    else:
        # get the image path from database 
        img_path = resultAll[5]
        # call the draw dish 
        processed_img_path = AST.draw_petri_dish(img_path)
        # save the path in the database for further processing 
        query = """UPDATE tests SET processed_image = %(processed_img_path)s WHERE id = %(test_id)s"""
        cursor.execute(query, {'processed_img_path': processed_img_path, 'test_id':test_id})
        test_id = cursor.lastrowid
        if test_id is None:
            return jsonify({"Status": "Failure", "Message": "Update failed"})
        mysql.connection.commit()
        cursor.close()
        # send the image 
        response = send_file(processed_img_path)
        return response