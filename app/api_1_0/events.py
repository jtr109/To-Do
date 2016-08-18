from flask import jsonify, request, g, url_for, current_app

from ..models import ListEvent
from . import api


@api.route('/events/<int:event_id>')
def get_event(event_id):
    event = ListEvent.query.get_or_404(event_id)
    return jsonify(event.to_json())


@api.route('/todo-lists/<int:list_id>/events/')
def get_todo_list_events(list_id):
    page = request.args.get('page', 1, type=int)
    pagination = ListEvent.query.filter_by(list_id=list_id).paginate(
        page, per_page=current_app.config['TODO_POSTS_PER_PAGE'],
        error_out=False)
    events = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_todo_list_events', list_id=list_id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_todo_list_events', list_id=list_id, page=page+1, _external=True)
    return jsonify({
        'todo_lists': [event.to_json() for event in events],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
