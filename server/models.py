from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
from sqlalchemy_serializer import SerializerMixin

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = relationship("Recipe", back_populates="user")

    @hybrid_property
    def password_hash(self):
        raise AttributeError("password_hash is not readable")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))
    
    def __repr__(self):
        return f'User {self.username}, ID: {self.id}, Bio: {self.bio}'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user = relationship("User", back_populates="recipes")

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title must be present")
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions:
            raise ValueError("Instructions must be present")
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return instructions
