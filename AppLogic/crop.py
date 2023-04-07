import os
import urllib.request
from flask import Flask, flash, request, redirect, send_file, Blueprint
from app import app
from werkzeug.utils import secure_filename
from AppLogic import AST as AST
import astimp
from imageio.v2 import imread, imwrite
from flask.json import jsonify

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

crop_blueprint = Blueprint("crop", __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""
    This route indicates an API endpoint, it recieves an image through post request. 
    The image is analyzed, its ROIs are extracted, cropped and saved to crop directory.
"""


@crop_blueprint.route('/process/crops', methods=['post'])
def analyze_image_crops():
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
    # check if the file exists and its extension is allowd
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # file is saved in the upload folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # save image to upload directory then process it to crops
        num_of_crops, data = AST.process_image_to_crops(filename)
        # prepare return data
        response_data = {'analysed crops': num_of_crops, 'crops details': data}
        return jsonify(response_data)


"""
     This route indicates an API endpoint, which recieves a request containing an image name and its path,
      then returns the image with this specific information,
"""


@crop_blueprint.route('/sendimg', methods=["POST"])
def send_img():
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
