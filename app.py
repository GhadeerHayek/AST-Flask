from flask import Flask

UPLOAD_FOLDER = 'static/uploads/'
CROP_FOLDER = 'static/crops/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CROP_FOLDER'] = CROP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024