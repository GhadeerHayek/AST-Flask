import os
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import AST as AST
import astimp
from imageio.v2 import imread, imwrite
from flask.json import jsonify


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

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
    This function receives a post request containing an image and returns JSON response 
    input: 
        image from request 
    output: 
        JSON response that contains each of the disks that were identified.
        This data includes:
            - label: the label of the disk 
            - CenterX: x coordinate of the disk in the image
            - centerY: y coordinate of the disk in the image 
            - radius: radius of the disk
            - diameter: inhibition zone diameter

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

if __name__ == "__main__":
    app.run(debug=True, host= '0.0.0.0', port=5000)
