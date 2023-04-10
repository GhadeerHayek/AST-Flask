"""
    App configurations can be found here. 
"""
class Config:
    SECRET_KEY = "antibiotics flask web service"
    UPLOAD_FOLDER = 'static/uploads/'
    CROP_FOLDER = 'static/crops/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # NOTE: the host ip must be changed according to the device's current ip
    MYSQL_HOST = '192.168.1.109'
    MYSQL_USER = 'WSL'
    MYSQL_PASSWORD = 'ayah_unix'
    # this is the name of our database
    MYSQL_DB = 'atb'