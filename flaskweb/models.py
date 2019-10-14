from flaskweb import db, login_manager

@login_manager.user_loader
def load_user(email):
    userjson = db.user.find_one({'email': email})
    if not userjson:
        return None
    return User(email=userjson['email'], username=userjson['username'])

class User:
    def __init__(self, email, username):
        self.email = email
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.email

# from flask_login import UserMixin

#
# class User(UserMixin):
#     def __init__(self, email):
#         self.email = email
