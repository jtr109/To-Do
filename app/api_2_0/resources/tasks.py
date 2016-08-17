from flask import jsonify, request, g, url_for
# flask-restful
from flask_restful import Resource, fields, marshal_with, reqparse
from app import restful_api

from ... import db
from ...models import Task
from .. import api2
from .errors import bad_request


post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'body', dest='body',
    location='json', required=True,
    help='The body of task',
)

task_fields = {
    'body': fields.String,
    'state': fields.String,
    'timestamp': fields.DateTime(dt_format='rfc822'),
    'todo_list': fields.String,
    'url': fields.String,
}

tasks_fields = {
    'todo_tasks': fields.Nested(task_fields),
    'doing_tasks': fields.Nested(task_fields),
    'done_tasks': fields.Nested(task_fields),
}


def jsonify_task(task):
    json_task = {
        'url': url_for('api.get_task', task_id=task.id, _external=True),
        'body': task.body,
        'state': task.state,
        'timestamp': task.timestamp,
        'todo_list': url_for('api.get_todo_list', list_id=task.list_id, _external=True),
    }
    return json_task


class TasksAPI(Resource):
    @marshal_with(tasks_fields)
    def get(self, list_id):
        todo_tasks = Task.query.filter_by(list_id=list_id, state='todo')
        doing_tasks = Task.query.filter_by(list_id=list_id, state='doing')
        done_tasks = Task.query.filter_by(list_id=list_id, state='done')
        return {
            'todo_tasks': [jsonify_task(todo_task) for todo_task in todo_tasks],
            'doing_tasks': [jsonify_task(doing_task) for doing_task in doing_tasks],
            'done_tasks': [jsonify_task(done_task) for done_task in done_tasks],
        }

restful_api.add_resource(TasksAPI, '/todo_lists/<int:list_id>/tasks/', endpoint='TasksAPI')


@api2.route('/todo_lists/<int:list_id>/tasks/', methods=['POST'])
def new_tasks(list_id):
    task = Task.from_json(request.json)
    task.list_id = list_id
    db.session.add(task)
    db.session.commit()
    return jsonify_task(task), 201, \
           {'Location': url_for('api.get_todo_list_tasks', list_id=list_id, _external=True)}  # todo: change url_for


'''
@api2.route('/todo_lists/<int:list_id>/tasks/')
def get_todo_list_tasks(list_id):
    todo_tasks = Task.query.filter_by(list_id=list_id, state='todo')
    doing_tasks = Task.query.filter_by(list_id=list_id, state='doing')
    done_tasks = Task.query.filter_by(list_id=list_id, state='done')
    return jsonify({
        'todo_tasks': [todo_task.to_json() for todo_task in todo_tasks],
        'doing_tasks': [doing_task.to_json() for doing_task in doing_tasks],
        'done_tasks': [done_task.to_json() for done_task in done_tasks],
    })
'''


class TaskAPI(Resource):
    @marshal_with(task_fields)
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        return jsonify_task(task)

restful_api.add_resource(TaskAPI, '/tasks/<int:task_id>', endpoint='TaskAPI')


'''
@api2.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_json())
'''


@api2.route('/tasks/<int:task_id>', methods=['PATCH'])
def change_state_of_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    todo_list = task.in_list
    list_id = todo_list.id
    if todo_list.master != g.current_user or task.in_list != todo_list:
        return bad_request('Invalid list.')
    state = request.json.get('state', task.state)
    if state not in ['todo', 'doing', 'done']:
        return bad_request('Invalid state')
    task.state = state
    db.session.add(task)
    return jsonify(task.to_json()), 202, \
        {'Location': url_for('api.get_todo_list', list_id=list_id, _external=True)}


@api2.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    todo_list = task.in_list
    list_id = todo_list.id
    if todo_list.master != g.current_user or task.in_list != todo_list:
        return bad_request('Invalid list.')
    db.session.delete(task)
    return jsonify(None), 303 ,\
           {'Location': url_for('api.get_todo_list', list_id=list_id, _external=True)}
