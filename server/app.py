#!/usr/bin/env python3

from flask import request, session
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource


from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        user = User(
            username=json['username'],
            password_hash=json['password'],
            image_url=json.get('image_url'),
            bio=json.get('bio')
        )
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username already exists.'}, 422
    

class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return user.to_dict(), 200
        else:
            return {'error': 'Unauthorized.'}, 401

    

class Login(Resource):
    def post(self):
        json = request.get_json()
        user = User.query.filter_by(username=json['username']).first()
        if user and user.authenticate(json['password']):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'error': 'Invalid username or password.'}, 401
    

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
            return {}, 204
        else:
            return {'error': 'Unauthorized.'}, 401
    

class RecipeIndex(Resource):
    def get(self):
        if 'user_id' in session:
            recipes = Recipe.query.all()
            return [recipe.to_dict() for recipe in recipes], 200
        else:
            return {'error': 'Unauthorized.'}, 401

    def post(self):
        if 'user_id' in session:
            json = request.get_json()
            recipe = Recipe(
                title=json['title'],
                instructions=json['instructions'],
                minutes_to_complete=json['minutes_to_complete'],
                user_id=session['user_id']
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        else:
            return {'error': 'Unauthorized.'}, 401

    

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
