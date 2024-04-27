from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import jsonify
from sqlalchemy.orm import backref
from datetime import datetime

bcrypt = Bcrypt()



db = SQLAlchemy()

# name: name
# type/subtype: types->0,1,...->type->name
# rarity: base_experience  (200+=SSR, 100-199=SR 0-99=R)
# image: sprites->front_default

#Palet town bg:
# https://pm1.narvii.com/6128/b08513b5aeaf14a72354b6d1ab234fa69cdf0f4a_hq.jpg
#gacha bg:
# https://i.ibb.co/mSvjMRh/pokemonspotlight.jpg
#pokeball: https://static.wikia.nocookie.net/pokemon/images/8/87/Pok%C3%A9_Ball.png
#greatball: https://static.wikia.nocookie.net/pokemon/images/a/ac/Great_Ball_Artwork.png
#ultraball: https://static.wikia.nocookie.net/pokemon/images/f/f1/UltraBallArt.png

def assign_rarity(num):
    """Return rarity based on numerical value."""
    if num <= 99:
        return 'R'
    if num < 200 and num > 99:
        return 'SR'
    if num >= 200:
        return 'SSR'
    
def format_move_name(txt):
    x = txt.rsplit("-")
    y = [ s.capitalize() for s in x ]
    z = " ".join(y)
    return z
    
class Pokemon(db.Model):
    """Pokemon."""

    __tablename__ = "pokemon"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)
    subtype = db.Column(db.Text, nullable=True)
    rarity = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)

    captures = db.relationship('Capture', backref='pokemon', lazy=True)
    moves = db.relationship('PokemonMove', backref='pokemon', lazy=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'subtype': self.subtype,
            'rarity': self.rarity,
            'image': self.image
        }
    
    def __repr__(self):
        if self.subtype:
            return f"[{self.rarity}] {self.name} ({self.type}/{self.subtype})"
        else:
            return f"[{self.rarity}] {self.name} ({self.type})"
        

class Move(db.Model):
    """Move."""

    __tablename__ = "moves"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    power = db.Column(db.Integer, nullable=False)
    pp = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Integer, nullable=False)

    owners = db.relationship('PokemonMove', backref='moves', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'power': self.power,
            'pp': self.pp,
            'accuracy': self.accuracy
        }

    def __repr__(self):
        return f"{self.name} - Power: {self.power}, PP Cost: {self.pp}, Hit Rate: {self.accuracy}%"
        

class User(db.Model):
    """User."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    
    captures = db.relationship('Capture', backref='users', lazy=True)
    
    @classmethod
    def register(cls, username, password):
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, password):
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

class Capture(db.Model):
    """Capture."""

    __tablename__ = "captures"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_captured = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))

class PokemonMove(db.Model):
    """Pokemon Move."""

    __tablename__ = "pokemon_moves"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
    move_id = db.Column(db.Integer, db.ForeignKey('moves.id'))


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
