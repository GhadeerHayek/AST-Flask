import os
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import AST as AST
import astimp
from imageio.v2 import imread, imwrite
from flask.json import jsonify
# for image response 
from flask import send_file
import base64
from io import BytesIO


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'jfif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# route that returns the upload images form.	
@app.route('/')
def upload_form():
	return render_template('upload.html')
# route the takes a post request - with an image -, renders the upload-form template with the processed image. 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        processed_file_name = AST.process_petri_dish(filename)
        return render_template('upload.html', filename=processed_file_name)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='processed/' + filename), code=301)

"""
    This route indicates to an API endpoint. The API is to receive an image through post request 
    and returns JSON response with each antibiotic data [label, center, radius, diameter] 
"""
@app.route('/api/imagedata', methods=['post'])
def analyze_image_data():
    # check if a file is sent in the request 
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # check if the file has a name 
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    # check if the file exists and its extension is allowd
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # file is saved in the upload folder 
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # process the image and prepare the data list
        mobile_list = AST.process_image(filename)
        # return JSON 
        return jsonify(mobile_list)
"""
    This route indicates an API endpoint, it recieves an image through post request. 
    The image is analyzed, its ROIs are extracted and cropped. 
    scenario is still abigious. 
"""
@app.route('/api/cropimage', methods=['post'])
def analyze_image_crops():
    # check if a file is sent in the request 
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # check if the file has a name 
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    # check if the file exists and its extension is allowd
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # file is saved in the upload folder 
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # NOTE: how are we going to return multiple images in a response? 
        # possible scenarios:
        # scenario 1: upload images on S3, let S3 handle your images. S3 shall prepare links for each image, return these links in your response.
        # scenario 2: create a table called attachments, each attachment has a unique id. Those list of IDs are returned in your response. 
        # when mobile needs to display an image, it would send a request to the backend to get this image with the ID of that image. 
       
        # NOTE: this code is for test purpose only, return one cropped image only 
        # TODO: if your cropped images were to be in a separate directory, then pay attention to the path of the opened image here. 
        data, images = AST.process_image_to_crops(filename)
        image_file = open(images[0], 'rb')      
        image_data = image_file.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        response_data = {'image':encoded_image, 'data':data[2]}
        
        return jsonify(response_data)

@app.route('/displayImg')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='processed/' + filename), code=301)



if __name__ == "__main__":
    app.run(debug=True, host= '0.0.0.0', port=5000)
