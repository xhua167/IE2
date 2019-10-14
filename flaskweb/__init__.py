from flask import Flask
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '4d7e72400c6b35d23f38678282d3ba5d'
uri = 'mongodb://umbsupportdb:1xcxH2Teq0O02cp8S7Pj4XSwXd0vqUgd56l9jPiWVm0ewsO0qTUPfNA9YHtoIBQMVmrP9M3twmyReKLff2NuoQ==@umbsupportdb.documents.azure.com:10255/?ssl=true&replicaSet=globaldb'
client = MongoClient(uri)
db = client.IE
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskweb import routes

