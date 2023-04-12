"""
    This class concerned with operations that manuiplate tests data, includes read, write and so. 
"""

from flask import Flask, Blueprint,jsonify
from werkzeug.utils import secure_filename
from database import mysql 
# routes blueprint
test_op_blueprint = Blueprint("test_op", __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""
    This API takes test data + authentication token as a parameter. Then, creates a test for the user in the database and returns its id.
    - Input: Bacteria, Sample type, name of the person who created the test 
    - Output: the newly created test id 

"""
@test_op_blueprint.route('/test/create', methods=['POST'])
def create_user_test():
    if 'file' not in request.files:
        # file not in create test request, reject it 
        pass
    # receive file 
    file = request.files['file']
    # if the file has no name -> don't procceed.
    if file.filename == '':
        # no image is selected for uploading
        pass 
    # check if the file exists and its extension is allowd
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # file is saved in the upload folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # perform processing 



"""
    This API is concerned with saving user adjustments on antibiotics labels and inhibition zone radius.
    - Input: json string which is a list of antibiotic objects, those objects contain the user adjustment on the original analysis data.
    - Output: test_id
"""
@test_op_blueprint.route('/test/confirmation', methods=['POST'])
#TODO
def save_user_adjustments():
    pass 