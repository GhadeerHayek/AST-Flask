import re 
import json
from database import mysql
# NOTE: for validating requests and inputs, there's a python library that could do this kind of thing called 'Marshmallow' 
# for every input you can write a set of validation rules 
# i guess it's for later
"""
    Checks if a give input is a required, non-empty, string
"""
def validate_string(input):
    if input is None:
        return False
    if not isinstance(input, str):
        return False
    if input == "":
        return False 
    try:
        int(input) 
        float(input)
        return False
    except ValueError:
        pass
    return True

def validate_email(input):
    valid_string = validate_string(input)
    if valid_string:
        match_result = re.match(r'^[A-Za-z0-9.-_%+]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',input)
        if match_result is None:
            return False
        else:
            return True
    else:
        return valid_string

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(file):
    if file is None:
        return False 
    if file.filename == "":
        return False 
    if not allowed_file(file.filename):
        return False 
    return True