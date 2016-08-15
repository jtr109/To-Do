from flask_restful import Resource

from app.models import User


class UserAPI(Resource):
    def get(self, user_id):
        return {'user' : 'test'}
        # user = User.query.get_or_404(user_id)
        # return user.to_json()

