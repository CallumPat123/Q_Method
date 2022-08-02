
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_manager
# flask admin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
# flask admin
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

LoginManager.login_view = 'login'

from app import routes, models, errors
