from flask import url_for
from flask_restful import Resource
from app import restful_api

from app.models import User


class Test(Resource):
    def get(self, id):
        return {'test': 'success'}

restful_api.add_resource(Test, '/test/<int:id>', endpoint='Test')


class AllUsersAPI(Resource):
    def get(self):
        users = User.query.all()
        users_link = map(lambda user: url_for('api2.UserAPI', user_id=user.id, _external=True), users)
        return {'users': users_link}

restful_api.add_resource(AllUsersAPI, '/users/', endpoint='AllUsersAPI')


class UserAPI(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user.to_json()

restful_api.add_resource(UserAPI, '/users/<int:user_id>', endpoint='UserAPI')
