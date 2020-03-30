from flask import Flask
from flask_socketio import SocketIO
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from initGame import GameRoom


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
socketio = SocketIO(app)
login = LoginManager(app)
login.login_view = 'login'
gameRoom = GameRoom()

from app import models, routes
