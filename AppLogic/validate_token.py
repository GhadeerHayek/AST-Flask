"""
    This class validates tokens
"""
from flask import current_app, request, jsonify
from datetime import datetime, timedelta
from AppLogic.token import verify_token
import jwt

def check_token_validity(token):
    # if there's no token -> halt process
    if not token:
        return jsonify({"Unauthorized": "No token"})
    # verify and decode the token 
    payload = verify_token(token, current_app.config['SECRET_KEY'])
    if isinstance(payload, dict):
        return payload
    else:
        return jsonify({"error": payload})