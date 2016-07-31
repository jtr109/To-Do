from flask import jsonify, request, g, url_for, current_app

from .. import db
from ..models import ToDoList
from . import api


@api.route('/todo_lists/<int:list_id>')
def get_todo_list(list_id):
    todo_list = ToDoList.query.get_or_404(list_id)
    return jsonify(todo_list.to_json())


@api.route('/todo_lists/')
def get_todo_lists():
    page = request.args.get('page', 1, type=int)
    pagination = ToDoList.query.filter_by(master=g.current_user).paginate(
        page, per_page=current_app.config['TODO_POSTS_PER_PAGE'],
        error_out=False)
    todo_lists = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_todo_lists', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_todo_lists', page=page+1, _external=True)
    return jsonify({
        'todo_lists': [t.to_json() for t in todo_lists],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/todo_lists/', methods=['POST'])
def create_todo_list():
    todo_list = ToDoList.from_json(request.json)
    todo_list.master = g.current_user
    db.session.add(todo_list)
    db.session.commit()
    return jsonify(todo_list.to_json()), 201, \
           {'Location': url_for('api.get_todo_list', list_id=todo_list.id, _external=True)}


@api.route('/todo_lists/<int:list_id>', methods=['DELETE'])
def delete_todo_list(list_id):
    todo_list = ToDoList.query.get_or_404(list_id)
    db.session.delete(todo_list)
    return jsonify({'Location': url_for('api.get_todo_lists', _external=True)})
