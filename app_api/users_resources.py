from flask import jsonify
from flask_restful import Resource, reqparse, abort

from data.users import User
from data import db_session


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


user_params = ('id', 'email', 'created_date')


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'users': user.to_dict(
            only=user_params)})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


# create user - UserListResource.post()
parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        for item in users:
            print(item)
        return jsonify({'users': [item.to_dict(
            only=user_params) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        users = session.query(User)
        if args['id'] in [i.id for i in users]:
            return jsonify({'error': 'Id already exists'})
        if args['email'] in [i.email for i in users]:
            return jsonify({'error': 'Email already exists'})
        user = User(
            id=args['id'],
            name=args['name'],
            about=args['about'],
            email=args['email'],
            city_from=args['city_from']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
