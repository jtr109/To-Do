from flask import jsonify, request, g, url_for, current_app

from ..models import ListEvent
from . import api


@api.route('/todo_lists/<int: list_id>/events/')
def get_events(list_id):
    page = request.args.get('page', 1, type=int)
    pagination = ListEvent.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        list_id=list_id, error_out=False)
    events = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_events', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_events', page=page+1, _external=True)
    return jsonify({
        'todo_lists': [event.to_json() for event in events],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
