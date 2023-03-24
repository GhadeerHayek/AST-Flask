"""
    test the new file structre and operations on database 
"""

import os
from app import app
from database import get_cursor, close_cursor
from flask.json import jsonify

@app.route('/', methods=['GET'])
def index():
    cursor = get_cursor()
    cursor.execute("select * from users")
    results = cursor.fetchall()
    close_cursor()
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, host= '0.0.0.0', port=5000)    