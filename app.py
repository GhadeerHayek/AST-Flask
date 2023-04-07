from flask import Flask
from flask_mysqldb import MySQL
from database import init_app
from config import Config

app = Flask(__name__)
# initialize app with database - i guess - 
init_app(app)

# app configurations from file 
app.config.from_object(Config)

# App routes blueprints 
from AppLogic.crop import crop_blueprint as crop_routes
from AppLogic.authentication import auth_blueprint as auth_routes
from AppLogic.user_operations import user_op_blueprint as user_op_routes

app.register_blueprint(crop_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(user_op_routes)