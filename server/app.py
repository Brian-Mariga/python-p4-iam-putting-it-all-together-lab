#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()

        user = User(
            username=json['username'],
            bio=json['bio'],
            image_url=json['image_url']
        )
        user.password_hash = json['password']

        try:
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return user.to_dict(), 201
        except IntegrityError as int:
            db.session.rollback()
            return {'error': f'{int}'}, 422

class CheckSession(Resource):
    def get(self):
        user =session['user_id']
        if user:
            details = User.query.get(user)
            return details.to_dict(), 200
        else:
            return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        json =request.get_json()

        username = json['username']
        password = json['password']

        if user := User.query.filter(User.username == username).first():
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200
            else:
                return {'message': 'Wrong password'}, 401
        else:
            return {'message': 'Invalid username'}, 401

class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id'] =None
            return {}, 204
        else:
            return {'error': 'Unauthorised'},401

class RecipeIndex(Resource):
    def get(self):
        if session['user_id']:
            recipes = Recipe.query.all()
            return {'recipes': [recipe.to_dict() for recipe in recipes]}, 200
        else:
            return {'error': 'Unauthorized'}, 401
        
    def post(self):

        request_json = request.get_json()

        title = request_json['title']
        instructions = request_json['instructions']
        minutes_to_complete = request_json['minutes_to_complete']

        try:

            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=session['user_id'],
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201

        except IntegrityError:

            return {'error': '422 Unprocessable Entity'}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)