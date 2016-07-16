from flask import jsonify, request, g, url_for

from .. import db
from ..models import ToDoList, Task
from . import api
from .errors import bad_request


@api.route('/todo_lists/<int:list_id>/tasks/')
def get_todo_list_tasks(list_id):
    todo_tasks = Task.query.filter_by(list_id=list_id, state='todo')
    doing_tasks = Task.query.filter_by(list_id=list_id, state='doing')
    done_tasks = Task.query.filter_by(list_id=list_id, state='done')
    return jsonify({
        'todo_tasks': [todo_task.to_json() for todo_task in todo_tasks],
        'doing_tasks': [doing_task.to_json() for doing_task in doing_tasks],
        'done_tasks': [done_task.to_json() for done_task in done_tasks],
    })


@api.route('/todo_lists/<int:list_id>/tasks/', methods=['POST'])
def new_tasks(list_id):
    task = Task.from_json(request.json)
    task.list_id = list_id
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_json()), 201, \
        {'Location': url_for('api.get_todo_list', id=list_id, _external=True)}


@api.route('/todo_lists/<int:list_id>/tasks/<int:task_id>', methods=['PUT'])
def change_state_of_task(list_id, task_id):
    todo_list = ToDoList.query.get_or_404(id=list_id)
    task = Task.query.filter_by(id=task_id)
    if todo_list.master != g.current_user or task.in_list != todo_list:
        return bad_request('Task not exist.')
    state = request.json.get('state', task.state)
    if state not in ['todo', 'doing', 'done']:
        return bad_request('Invalid state')
    task.state = state
    db.session.add(task)
    return jsonify(task.to_json()), 201, \
        {'Location': url_for('api.get_todo_list', id=list_id, _external=True)}


@api.route('/todo_lists/<int:list_id>/tasks/<int:id>', methods=['DELETE'])
def delete_task(list_id, id):
    todo_list = ToDoList.query.get_or_404(id=list_id)
    task = Task.query.filter_by(id=id)
    if todo_list.master != g.current_user or task.in_list != todo_list:
        return bad_request('Task not exist.')
    state = request.get('state', task.state)
    if state not in ['todo', 'doing', 'done']:
        return bad_request('Invalid state')
    db.session.delete(task)
    return jsonify({'Location': url_for('api.get_todo_list', id=list_id, _external=True)})