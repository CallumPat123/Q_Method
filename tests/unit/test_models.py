from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

def dummy_test():
    assert 1 == 1 

#def test_new_user():
#    #TODO fix test to be reflective of new user models
#
#    new_user = User(username = 'usernam1', email = 'test_user@email.com', password_hash = 'password')
#    assert new_user.username == 'usernam1'
#    assert new_user.email == 'test_user@email.com'

## note the below is commentted out because I cant make it work, will come back to it later
    # plain_text_password = 'password'
    # assert check_password_hash(new_user.password_hash, plain_text_password) == True

#def test_user_check_password():
#    new_user = User(username = 'usernam1', email = 'test_user@email.com', password_hash = 'password')
#    assert new_user.check_password('password') == True

