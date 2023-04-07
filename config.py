"""
    App configurations can be found here. 
"""
class Config:
    SECRET_KEY = "antibiotics flask web service"
    UPLOAD_FOLDER = 'static/uploads/'
    CROP_FOLDER = 'static/crops/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # NOTE: the host ip must be changed according to the device's current ip
    MYSQL_HOST = '192.168.0.101'
    MYSQL_USER = 'WSL_USER'
    MYSQL_PASSWORD = ''
    # this is the name of our database
    MYSQL_DB = 'antibiotics_project'