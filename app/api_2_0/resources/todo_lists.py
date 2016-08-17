from flask import request, g, url_for, current_app
# flask-restful
from flask_restful import Resource, fields, marshal_with, reqparse
from .. import restful_api

from ... import db
from ...models import ToDoList

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'title', dest='title',
    location='json', required=True,
    help='The title of list',
)

todo_list_fields = {
    'events': fields.String,
    'master': fields.String,
    'tasks': fields.String,
    'timestamp': fields.DateTime(dt_format='rfc822'),
    'title': fields.String,
    'url': fields.String,
}

todo_lists_fields = {
    'count': fields.Integer,
    'next': fields.String,
    'prev': fields.String,
    'todo_lists': fields.Nested(todo_list_fields),
}


class TodoListsAPI(Resource):
    @marshal_with(todo_lists_fields)
    def get(self):
        page = request.args.get('page', 1, type=int)
        pagination = ToDoList.query.filter_by(master=g.current_user).paginate(
            page, per_page=current_app.config['TODO_POSTS_PER_PAGE'],
            error_out=False)
        todo_lists = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api2.TodoListsAPI', page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api2.TodoListsAPI', page=page+1, _external=True)
        return {
            'todo_lists': [t.to_json(version='2.0') for t in todo_lists],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }

    @marshal_with(todo_list_fields)
    def post(self):
        args = post_parser.parse_args()
        print("args.title is %r" % args.title)
        # request: {'title=example title'}
        master = g.current_user
        todo_list = ToDoList.create_new(title=args.title, master=master)
        return todo_list.to_json(version='2.0'), 201

restful_api.add_resource(TodoListsAPI, '/todo_lists/', endpoint='TodoListsAPI')


class TodoListAPI(Resource):
    @marshal_with(todo_list_fields)
    def get(self, list_id):
        todo_list = ToDoList.query.get_or_404(list_id)
        return todo_list.to_json()

    def delete(self, list_id):
        todo_list = ToDoList.query.get_or_404(list_id)
        db.session.delete(todo_list)
        return '', 303, \
            {'Location': url_for('api.get_todo_lists', _external=True)}

restful_api.add_resource(TodoListAPI, '/todo_lists/<int:list_id>', endpoint='TodoListAPI')

