from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from json import dumps, loads


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    player_sid = db.Column(db.String(64), index=True, unique=True, nullable=True)
    password_hash = db.Column(db.String(128))
    in_room = db.Column(db.String(4), db.ForeignKey('room.roomID'), nullable=True)
    order = db.Column(db.Integer, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # check password sting against hash in database
        return(check_password_hash(self.password_hash, password))

    def __repr(self):
        return('<User {}>'.format(self.username))


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomID = db.Column(db.String(4), index=True, unique=True)
    owner_id = db.Column(db.Integer)
    players = db.relationship('User', backref='room', lazy='dynamic')
    JSON_string = db.Column(db.JSON, nullable=True)

    def set_JSON(self, MJgame):
        self.JSON_string = dumps(MJgame.__dict__)

    def load_JSON(self):
        return(loads(self.JSON_string))


@login.user_loader
def load_user(id):
    return(User.query.get(int(id)))
