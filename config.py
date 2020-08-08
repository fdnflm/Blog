import os
""" SET CONFIGURATION """
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = False

CSRF_ENABLED = True
CSRF_SESSION_KEY = "secret"
SECRET_KEY = "secret"

DEBUG = True
UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "test@gmail.com"
MAIL_PASSWORD = "test"
MAIL_DEFAULT_SENDER = "test@gmail.com"

TELEGRAM_TOKEN = ""
CHANNEL_ID = ""
