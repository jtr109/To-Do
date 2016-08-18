from flask import jsonify, request, g, url_for

from .. import db
from ..models import Task
from . import api
from .errors import bad_request


@api.route('/todo-lists/<int:list_id>/tasks/', methods=['POST'])
def new_tasks(list_id):
    task = Task.from_json(request.json)
    task.list_id = list_id
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_json()), 201, \
           {'Location': url_for('api.get_todo_list_tasks', list_id=list_id, _external=True)}


@api.route('/todo-lists/<int:list_id>/tasks/')
def get_todo_list_tasks(list_id):
    todo_tasks = Task.query.filter_by(list_id=list_id, state='todo')
    doing_tasks = Task.query.filter_by(list_id=list_id, state='doing')
    done_tasks = Task.query.filter_by(list_id=list_id, state='done')
    return jsonify({
        'todo_tasks': [todo_task.to_json() for todo_task in todo_tasks],
        'doing_tasks': [doing_task.to_json() for doing_task in doing_tasks],
        'done_tasks': [done_task.to_json() for done_task in done_tasks],
    })


@api.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_json())


@api.route('/tasks/<int:task_id>', methods=['PUT'])
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


@api.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    todo_list = task.in_list
    list_id = todo_list.id
    if todo_list.master != g.current_user or task.in_list != todo_list:
        return bad_request('Invalid list.')
    db.session.delete(task)
    return jsonify(None), 303 ,\
           {'Location': url_for('api.get_todo_list', list_id=list_id, _external=True)}
