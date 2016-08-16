from flask import jsonify, request, g, url_for, current_app
# flask-restful
from flask_restful import Resource, fields, marshal_with
from .. import restful_api

from ... import db
from ...models import ToDoList
from .. import api2

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
            prev = url_for('api2.resource.TodoListsAPI', page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api2.resource.TodoListsAPI', page=page+1, _external=True)
        return {
            'todo_lists': [t.to_json() for t in todo_lists],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }

'''
    def post(self):
        # request: {'title': 'example title'}
        todo_list = ToDoList.from_json(request.json)
        todo_list.master = g.current_user
        db.session.add(todo_list)
        db.session.commit()
        return todo_list.to_json(), 201  # , \
               # {'Location': url_for('api2.get_todo_list', list_id=todo_list.id, _external=True)}
'''
restful_api.add_resource(TodoListsAPI, '/todo_lists/', endpoint='TodoListsAPI')


"""
@api2.route('/todo_lists/', methods=['POST'])
def create_todo_list():
    todo_list = ToDoList.from_json(request.json)
    todo_list.master = g.current_user
    db.session.add(todo_list)
    db.session.commit()
    return jsonify(todo_list.to_json()), 201, \
           {'Location': url_for('api.get_todo_list', list_id=todo_list.id, _external=True)}
"""


class TodoListAPI(Resource):
    @marshal_with(todo_list_fields)
    def get(self, list_id):
        todo_list = ToDoList.query.get_or_404(list_id)
        return todo_list.to_json()

restful_api.add_resource(TodoListAPI, '/todo_lists/<int:list_id>', endpoint='TodoListAPI')


@api2.route('/todo_lists/<int:list_id>', methods=['DELETE'])
def delete_todo_list(list_id):
    todo_list = ToDoList.query.get_or_404(list_id)
    db.session.delete(todo_list)
    return jsonify(None), 303, \
           {'Location': url_for('api.get_todo_lists', _external=True)}
