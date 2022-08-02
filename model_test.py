from app import db
from app.models import *
from werkzeug.security import generate_password_hash
import datetime

###This file will:
# create a test role
# create a user with test role
# create surveys belonging to the user

def test_function():
    """A function that creates a sample role, user, and commits them to the db
    created to test that python can write data to db"""

    #populate the DB with the above data
    print("Starting sample test script")

    #Check if test role already in DB
    if(Role.query.filter_by(name = 'test').first() == None):
        # Create a test role
        test_role = Role("test")
        db.session.add(test_role)
    else:
        test_role = Role.query.filter_by(name = 'test').first()

    #Check if test user already in DB
    if(User.query.filter_by(email = "test@email.com").first() == None):
    # Create a test user for this script
        test_user = User(email= "test@email.com", username= "TU", password_hash ="abc123", 
                first_name = "te", last_name = "st", role = test_role)
        db.session.add(test_user)
    
    
    db.session.commit()


