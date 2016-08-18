from flask import g, url_for
# flask-restful
from flask_restful import Resource, fields, marshal_with, reqparse
from app import restful_api

from ... import db
from ...models import Task, ToDoList, User
from .errors import bad_request, unauthorized


post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'body', dest='body',
    location='json', required=True,
    help='The body of task',
)

state_parser = reqparse.RequestParser()
state_parser.add_argument(
    'state', dest='state',
    choices=('todo', 'doing', 'done',),
    location='json', required=True,
    help='The state of task (todo, doing, done)',
)

task_fields = {
    'body': fields.String,
    'state': fields.String,
    'timestamp': fields.DateTime(dt_format='rfc822'),
    'todo_list': fields.String,
    'url': fields.String,
}

tasks_fields = {
    'url': fields.String,
    'todo_tasks': fields.Nested(task_fields),
    'doing_tasks': fields.Nested(task_fields),
    'done_tasks': fields.Nested(task_fields),
}


def to_json_task(task):
    json_task = {
        'url': url_for('api2.TaskAPI', task_id=task.id, _external=True),
        'body': task.body,
        'state': task.state,
        'timestamp': task.timestamp,
        'todo_list': url_for('api2.TodoListAPI', list_id=task.list_id, _external=True),
    }
    return json_task


class TasksAPI(Resource):
    @marshal_with(tasks_fields)
    def get(self, list_id):
        todo_list = ToDoList.query.get_or_404(list_id)
        if todo_list.master != g.current_user:
            return unauthorized("Invalid User.")
        todo_tasks = Task.query.filter_by(list_id=list_id, state='todo')
        doing_tasks = Task.query.filter_by(list_id=list_id, state='doing')
        done_tasks = Task.query.filter_by(list_id=list_id, state='done')
        return {
            'url': url_for('api2.TasksAPI', list_id=list_id, _external=True),
            'todo_tasks': [to_json_task(todo_task) for todo_task in todo_tasks],
            'doing_tasks': [to_json_task(doing_task) for doing_task in doing_tasks],
            'done_tasks': [to_json_task(done_task) for done_task in done_tasks],
        }

    @marshal_with(task_fields)
    def post(self, list_id):
        args = post_parser.parse_args()
        todo_list = ToDoList.query.get_or_404(list_id)
        if todo_list.master != g.current_user:
            return unauthorized("Invalid User.")
        task = Task(body=args.body, list_id=list_id)
        db.session.add(task)
        db.session.commit()
        return to_json_task(task), 201

restful_api.add_resource(TasksAPI, '/todo_lists/<int:list_id>/tasks/', endpoint='TasksAPI')


class TaskAPI(Resource):
    @marshal_with(task_fields)
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        return to_json_task(task)

    @marshal_with(task_fields)
    def put(self, task_id):
        args = state_parser.parse_args()
        task = Task.query.filter_by(id=task_id).first()
        if task.in_list.master != g.current_user:
            return unauthorized('Invalid master.')
        task.state = args.state
        db.session.add(task)
        db.session.commit()
        return to_json_task(task), 202, \
            {'Location': url_for('api2.TodoListAPI', list_id=task.list_id, _external=True)}

    def delete(self, task_id):
        task = Task.query.filter_by(id=task_id).first()
        if task.in_list.master != g.current_user:
            return unauthorized('Invalid master.')
        db.session.delete(task)
        return None, 303, \
            {'Location': url_for('api2.TasksAPI', list_id=task.list_id, _external=True)}

restful_api.add_resource(TaskAPI, '/tasks/<int:task_id>', endpoint='TaskAPI')
