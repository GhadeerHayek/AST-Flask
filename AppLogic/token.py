"""
    This class is concerned with the authentication token 
"""
from flask import current_app, request, jsonify
from datetime import datetime, timedelta
import jwt


""" 
    Generates a token for authentication. 
    It should use a module that i currently can't remeber its name 
    It take a parameter, that is the user row in the database, encrypts it, and returns its hash.
"""


def generate_token(user_record, secret_key):
    # when do we want the token to be expired?
    # initially, let's make it 2 hours
    exp_time = datetime.utcnow() + timedelta(hours=1)
    # prepare payload
    token_payload = {
        "id": user_record[0],
        "name": user_record[1],
        "email": user_record[2],
        "password": user_record[3],
        "expire": exp_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    # generate token
    token = jwt.encode(
        token_payload, secret_key, algorithm='HS256')
    return token

"""
    takes in a token, returns the encrypted data within it. 
    So if we assume we've encrypted the user's row in the database, this shall retrieve it. 
"""


def verify_token(token, secret_key):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        # if it reaches this line, this means that it's decoded correctly
        # check expiration time
        if 'expire' in payload:
            exp_time = datetime.strptime(payload['expire'], '%Y-%m-%d %H:%M:%S')
            if datetime.utcnow() > exp_time:
                return False
            else: 
                # token not expired and return data  
                payload = {
                    "id": payload["id"],
                    "name": payload["name"],
                    "email": payload["email"],
                }
                return payload
        else:
            return False 
    except jwt.exceptions.DecodeError:
        # if it reaches this line, this means that it's decoded incorrectly
        return False

"""
    Helper function that checks the token to authorize the user
"""
def authorize_user(token):
    # if there's no token -> halt process
    if not token:
        return jsonify({"Status":"Failure", "Message":"Unauthorized, no token"})
    # verify and decode the token 
    payload = verify_token(token, current_app.config['SECRET_KEY'])
    if isinstance(payload, dict):
        return payload
    else:
        return jsonify({"Status":"Failure", "Message": "User is not authorized."})
