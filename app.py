from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager
from flask_migrate import Migrate
#from flask_mobility import Mobility
from flask_moment import Moment
from flask_mail import Mail
from config import TELEGRAM_TOKEN
from misc import Telegram_API
""" INITIALIZE ALL INSTANCES """
app = Flask(__name__)
app.config.from_object('config')
login_manager = LoginManager(app)
login_manager.login_view = "login"
db = SQLAlchemy(app)
api = Telegram_API(TELEGRAM_TOKEN)
#Mobility(app)
moment = Moment(app)
migrate = Migrate(app, db)
mail = Mail(app)
