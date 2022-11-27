###
#   module:     globals.py   
#   Sharing global variables (and other) across modules
###

from flask_cors import CORS
from flask import Flask
from datetime import timedelta
from flask_login import LoginManager

INACTIVITY_LOGOUT_HOURS = 2
INACTIVITY_LOGOUT_MINUTES = 0
INACTIVITY_LOGOUT_SECONDS = 0
INACTIVITY_LOGOUT_TIME = INACTIVITY_LOGOUT_SECONDS + INACTIVITY_LOGOUT_MINUTES*60 + INACTIVITY_LOGOUT_HOURS*3600

# App Core
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://efemscpqmxlctp:4fbe8cae307b501ce9e0c84a5d08245586f9fe94971e752ab26a2c9a48722be2@ec2-54-170-90-26.eu-west-1.compute.amazonaws.com:5432/dq1dfkpr05s3r'
#app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "postgres"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=INACTIVITY_LOGOUT_TIME)

# Login
loginManager = LoginManager()
loginManager.init_app(app)

# User Data
user_logged_in = False          #   is user logged in?
logged_user = None              #   logged user data
nav_current_page = "index"      #   current opene page for navbar
nav_pages = []                  #   list of pages in navigation bar
path = []                       #   current navigation path
last_url = None                 #   last visited URL shared element
logged_users = []               #   list of logged users
temp_cart = []                  #   temporary cart
