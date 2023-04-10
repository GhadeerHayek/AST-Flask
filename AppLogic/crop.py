import os, astimp, jwt
from flask import Flask, flash, request, redirect, send_file, Blueprint, current_app, jsonify
from app import app
from werkzeug.utils import secure_filename
from AppLogic import AST as AST
from AppLogic.token import verify_token
from database import mysql

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

crop_blueprint = Blueprint("crop", __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""
    This route indicates an API endpoint, it recieves an image through post request. 
    The image is analyzed, its ROIs are extracted, cropped and saved to crop directory.
"""


@crop_blueprint.route('/process/crops', methods=['POST'])
def analyze_image_crops():
    # using the "access_token" which was set at login to authorize the user's request
    token = request.cookies["access_token"]
    # if there's not token -> halt process
    if not token:
        return jsonify({"Unauthorized": "No token"})
    # verify and decode the token 
    payload = verify_token(token, current_app.config['SECRET_KEY'])
    if isinstance(payload, dict):
        # get user id for later usage
        user_id = payload["id"]
        cursor = mysql.connection.cursor()
        #  if a file is not sent in the request -> don't procceed.
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        # if a file key exists, then fetch the file from the request
        file = request.files['file']
        # if the file has no name -> don't procceed.
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        # check if the file exists and its extension is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # get the file as paren_dir fir the crops and create it in the system
            parent_dir = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(parent_dir)
            # prepare return data
            num_of_crops, data = AST.process_image_to_crops(filename)
            # prepare sql statement
            query = "INSERT INTO cropped_antibiotics (test_id, path, parent_directory) VALUES (%s, %s, %s)"
            result = ""
            # loop through each antibiotic to insert it to db  
            for atb in data:
                values = (1, atb["img_folder"], parent_dir )
                result = cursor.execute(query, values)
            # user commit to make the insertion permenant
            mysql.connection.commit()
            cursor.close()
            if result:
                # success -> return all atb details to mobile
                response_data = {'analysed crops': num_of_crops, 'crops details': data}           
                return jsonify(response_data)
    else:
        return jsonify({"error": payload})
    


"""
     This route indicates an API endpoint, which recieves a request containing an image name and its path,
      then returns the image with this specific information,
"""


@crop_blueprint.route('/fetch/crop', methods=['POST'])
def get_crop():
    # if image name and its path not in the request -> don't procceed.
    if 'img_name' not in request.form and 'img_path' not in request.form:
        return "No image is provided!"
    # fetch image name and path from the request
    img_name = request.form['img_name']
    img_path = request.form['img_path']
    # if the image name or its path are empty -> don't procceed.
    if img_name == '' or img_path == '':
        # img_name is dummy -> not acceptable
        return "Blank/empty images are not acceptable!"
    # but if it exists and its extension is allowed
    if img_name and allowed_file(img_name):
        # fetch the image specified, and send it.
        img = os.path.join(img_path, img_name)
        return send_file(img)

@crop_blueprint.route('/')
def mock_route():
    return "Hello World?"
