from flask_restful import Resource
from app import restful_api

from app.models import User


class Test(Resource):
    def get(self, id):
        return {'test': 'success'}

restful_api.add_resource(Test, '/test/<int:id>')

# class UserAPI(Resource):
#     def get(self, user_id):
#         return {'user' : 'test'}
#         # user = User.query.get_or_404(user_id)
#         # return user.to_json()

