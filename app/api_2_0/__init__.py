from flask import Blueprint

api2 = Blueprint('api2', __name__)

from app import restful_api
restful_api.init_app(api2)

from .resources import users
