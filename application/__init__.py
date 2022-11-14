from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin,current_user, login_required, login_user, logout_user
from models import *
from os import path
from string import ascii_lowercase, ascii_uppercase
from flask_bcrypt import Bcrypt
from datetime import datetime
from validation import InputError, ServerError

app = Flask(__name__, template_folder="../templates", static_url_path='', static_folder="../static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../projectdb.sqlite3'
app.secret_key = "myapp123"

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user_login"


app.app_context().push()
logged_in_as = ""

from application import tracker
from application import user
from application import log


