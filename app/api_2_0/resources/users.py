from flask import url_for
from flask_restful import Resource, fields, marshal_with
from app import restful_api

from app.models import User

user_fields= {
    'url': fields.String,
    'username': fields.String,
    'todo_lists': fields.String,
}


class AllUsersAPI(Resource):
    def get(self):
        users = User.query.all()
        users_link = map(lambda user: url_for('api2.UserAPI', user_id=user.id, _external=True), users)
        return {'users': users_link}

restful_api.add_resource(AllUsersAPI, '/users/', endpoint='AllUsersAPI')


class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        user_info = user.get_info()  # 'user_id', 'username'
        user_json = {
            'url': url_for('api2.UserAPI', user_id=user_info['user_id'], _external=True),
            'username': user_info['username'],
            'todo_lists': url_for('api2.TodoListsAPI', _external=True),
        }
        return user_json

restful_api.add_resource(UserAPI, '/users/<int:user_id>', endpoint='UserAPI')
