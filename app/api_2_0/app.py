# !/usr/bin/env python

# from flask import Flask
import flask_restful
from resources.users import UserAPI
from .. import restful_api

# app = Flask(__name__)
# api = flask_restful.Api(app)

restful_api.add_resource(UserAPI, '/users', '/users/<str:id>')
