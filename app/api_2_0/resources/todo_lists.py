from flask import request, g, url_for, current_app
# flask-restful
from flask_restful import Resource, fields, marshal_with, reqparse
from app import restful_api

from ... import db
from ...models import ToDoList

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'title', dest='title',
    location='json', required=True,
    help='The title of list',
)

todo_list_fields = {
    'url': fields.String,
    'title': fields.String,
    'timestamp': fields.DateTime(dt_format='rfc822'),
    'master': fields.String,
    'tasks': fields.String,
    'events': fields.String,
}

todo_lists_fields = {
    'todo_lists': fields.Nested(todo_list_fields),
    'count': fields.Integer,
    'prev': fields.String,
    'next': fields.String,
}


def jsonify_todo_list(todo_list):
    json_todo_list = {
        'url': url_for('api2.TodoListAPI', list_id=todo_list.id, _external=True),
        'title': todo_list.title,
        'timestamp': todo_list.timestamp,
        'master': url_for('api2.UserAPI', user_id=todo_list.master_id, _external=True),
        'tasks': url_for('api.get_todo_list_tasks', list_id=todo_list.id, _external=True),
        'events': url_for('api.get_todo_list_events', list_id=todo_list.id, _external=True),
    }
    return json_todo_list


class TodoListsAPI(Resource):
    @marshal_with(todo_lists_fields)
    def get(self):
        page = request.args.get('page', 1, type=int)
        pagination = ToDoList.query.filter_by(master=g.current_user).\
            order_by(ToDoList.timestamp.desc()).paginate(
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
            'todo_lists': [jsonify_todo_list(t) for t in todo_lists],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }

    @marshal_with(todo_list_fields)
    def post(self):
        args = post_parser.parse_args()
        master = g.current_user
        todo_list = ToDoList.create_new(title=args.title, master=master)
        return jsonify_todo_list(todo_list), 201

restful_api.add_resource(TodoListsAPI, '/todo_lists/', endpoint='TodoListsAPI')


class TodoListAPI(Resource):
    @marshal_with(todo_list_fields)
    def get(self, list_id):
        todo_list = ToDoList.query.get_or_404(list_id)
        return jsonify_todo_list(todo_list)

    def delete(self, list_id):
        todo_list = ToDoList.query.get_or_404(list_id)
        db.session.delete(todo_list)
        return '', 303, \
            {'Location': url_for('api.get_todo_lists', _external=True)}

restful_api.add_resource(TodoListAPI, '/todo_lists/<int:list_id>', endpoint='TodoListAPI')

