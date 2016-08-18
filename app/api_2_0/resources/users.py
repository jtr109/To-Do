from flask import url_for
from flask_restful import Resource, fields, marshal_with
from app import restful_api

from app.models import User
from .errors import unauthorized

user_fields= {
    'url': fields.String,
    'username': fields.String,
    'todo_lists': fields.String,
}


def to_json_user(user):
    user_json = {
        'url': url_for('api2.UserAPI', user_id=user.id, _external=True),
        'username': user.username,
        'todo_lists': url_for('api2.TodoListsAPI', _external=True),
    }
    return user_json


'''
# should be removed in prod env
class AllUsersAPI(Resource):
    def get(self):
        users = User.query.all()
        users_url = map(lambda user: url_for('api2.UserAPI', user_id=user.id, _external=True), users)
        return {'users': users_url}

restful_api.add_resource(AllUsersAPI, '/users/', endpoint='AllUsersAPI')
'''


'''
class TestAPI(Resource):
    def get(self):
        return unauthorized("Invalid User.")

restful_api.add_resource(TestAPI, '/test', endpoint='TestAPI')
'''


class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        if user != g.current_user:
            return unauthorized("Invalid User.")
        return to_json_user(user)

restful_api.add_resource(UserAPI, '/users/<int:user_id>', endpoint='UserAPI')
