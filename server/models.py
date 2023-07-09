# !/usr/bin/env python3

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
# we import validates
from sqlalchemy.orm import validates
from config import db, bcrypt


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=False)
    bio = db.Column(db.String, nullable=False)
    recipes = db.relationship("Recipe", backref="user")

    
    # Attempts to access the password_hash should be met with an AttributeError
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Cant view hashed password.")
    
    # incorating bcrypt for secure password
    @password_hash.setter
    def password_hash(self, password):
        password_hash=bcrypt.generate_password_hash(password.encode("utf-8"))
        self._password_hash=password_hash.decode("utf-8")

    # validate the user's username to ensure that it is present and unique (no two users can have the same username).
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash,password.encode("utf-8"))
        
     
        
        
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


    # Add validations title must be present
    @validates("title")
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Tittle must be present.")
        return title

    # Add validations instructions must be present and at least 50 characters long
    @validates("instructions")
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:
            raise ValueError("Instructions must be present and at least 50 characters long.")
        return instructions
        
    







# ....learning..
# validates works when trying to load data in the database the validates 
# creates and deletes all records from the tables to raise the error
# when running seed.py the validation is working 
# being able to raise the errors (Title must be present)
# raise ValueError("Tittle must be present.")
# ValueError: Tittle must be present.


# #     raise ValueError("Instructions must be present and at least 50 characters long.")
# ValueError: Instructions must be present and at least 50 characters long.


# flask db init
# flask db migrate -m "Initial migration"
# flask db upgrade