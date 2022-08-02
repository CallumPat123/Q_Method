from app import routes, models, errors
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager, login_manager
from flask_script import Manager
import io
import xlwt
import os
import model_test
from flask_fontawesome import FontAwesome

app = Flask(__name__)
fa = FontAwesome(app)
app.config.from_object(os.environ['APP_SETTINGS'])
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize db
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

login = LoginManager(app)
login.login_view = 'login'


if __name__ == '__main__':
    app.debug = True
    app.run()

with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

# only admin creates users, registerable disabled
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_REGISTERABLE'] = False
app.config['SECURITY_RECOVERABLE'] = True
