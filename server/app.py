#!/usr/bin/env python3

from flask import request, session
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json_info = request.get_json()
        username = json_info.get('username')
        password = json_info.get('password')
        image_url = json_info.get('image_url')
        bio = json_info.get('bio')
        
        user = User(
            username=username,
            password=password,
            image_url=image_url,
            bio=bio
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
            user_id = session['user_id']
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {'error': 'Unauthorized.'}, 401
    

class Login(Resource):
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
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
            user_id = session['user_id']
            recipes = Recipe.query.filter_by(user_id=user_id).all()
            return [recipe.to_dict() for recipe in recipes], 200
        else:
            return {'error': 'Unauthorized.'}, 401

    def post(self):
        if 'user_id' in session:
            json = request.get_json()
            title = json.get('title')
            instructions = json.get('instructions')
            minutes_to_complete = json.get('minutes_to_complete')
            
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
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
