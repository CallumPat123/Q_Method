import os
from dotenv import load_dotenv, find_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))

#dotenv_path = join(dirname(__file__), '.env')
load_dotenv(find_dotenv())

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_SERVER = os.getenv('DB_SERVER')
DB_PORT = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE')

if(DB_USERNAME is None):
    # Implies a .ENV file was not loaded, assume production server
    FLASK_ENV = "production"
else:
    FLASK_ENV = "development"


class Config(object):
    # Secrets
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Setup SQLAlchemy
    if(FLASK_ENV == "production"):
        # Connect to heroku DB
        SQLALCHEMY_DATABASE_URL = os.getenv(
            "DATABASE_URL").replace('postgres://', 'postgresql://')
    elif(FLASK_ENV == "development"):
        ##FLASK_ENV = developement
        # Create Alternative / Local DB URL
        alternative_db_url = ""
        alternative_db_url = "postgresql://" + DB_USERNAME + ":" + DB_PASSWORD \
            + "@" + DB_SERVER + ":" + DB_PORT + "/" + DB_DATABASE

        SQLALCHEMY_DATABASE_URL = alternative_db_url

    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URL

    # alternative_db_uri
    # TODO confirm this works on all local machines and heroku
    # Was previously 'postgrelsql:// + ' os.path.join(basedir, 'app.db'),
    # I litterally have no clue how any of this works - LEigh
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# import os
# from dotenv import load_dotenv, find_dotenv


# basedir = os.path.abspath(os.path.dirname(__file__))

# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)

# DB_USERNAME = os.getenv('DB_USERNAME')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_SERVER = os.getenv('DB_SERVER')
# DB_PORT = os.getenv('DB_PORT')
# DB_DATABASE = os.getenv('DB_DATABASE')

# if(DB_USERNAME is None):
#     #Implies a .ENV file was not loaded, assume production server
#     FLASK_ENV = "production"
# else:
#     FLASK_ENV = "development"


# class Config(object):
#     # Secrets
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

#     # Setup SQLAlchemy
#     if(FLASK_ENV == "production"):
#         #Connect to heroku DB
#         SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL").replace('postgres://', 'postgresql://')
#     elif(FLASK_ENV == "development"):
#         ##FLASK_ENV = developement
#         # Create Alternative / Local DB URL
#         alternative_db_url = ""
#         alternative_db_url = "postgresql://" +  DB_USERNAME + ":"+ DB_PASSWORD \
#                      + "@" + DB_SERVER + ":" + DB_PORT  + "/" + DB_DATABASE

#         SQLALCHEMY_DATABASE_URL = alternative_db_url
#     SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URL
#         #alternative_db_uri
#         #TODO confirm this works on all local machines and heroku
#         #Was previously 'postgrelsql:// + ' os.path.join(basedir, 'app.db'),
#         #I litterally have no clue how any of this works - LEigh
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
