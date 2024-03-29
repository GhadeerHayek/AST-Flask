import re
import json
from database import mysql

"""
    validate_string() checks if a given input is a required, non-empty, string
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


"""
    validate_email() calls for validate_string() to check the input,
     checks if the given string format matches the regex of emails format. 
"""


def validate_email(input):
    valid_string = validate_string(input)
    if valid_string:
        match_result = re.match(
            r'^[A-Za-z0-9.-_%+]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', input)
        if match_result is None:
            return False
        else:
            return True
    else:
        return valid_string


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'jfif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""
    validate_file() checks if a given file is not empty, and its extension is allowed
"""


def validate_file(file):
    if file is None:
        return False
    if file.filename == "":
        return False
    if not allowed_file(file.filename):
        return False
    return True

def create_message(status, message):
    return jsonify({"Status": "{}".format(status), "Message": "{}".format(message)}) 