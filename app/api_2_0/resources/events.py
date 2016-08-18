from flask import jsonify, request, g, url_for, current_app
# flask-restful
from flask_restful import Resource, fields, marshal_with, reqparse
from app import restful_api

from ...models import ListEvent
from .. import api2

event_fields = {
    'url': fields.String,
    'event': fields.String,
    'timestamp': fields.DateTime(dt_format='rfc822'),
    'todo_list': fields.String,
}


def jsonify_event(event):
    json_event = {
        'url': url_for('api.get_event', event_id=event.id, _external=True),
        'event': event.event,
        'timestamp': event.timestamp,
        'todo_list': url_for('api.get_todo_list', list_id=event.list_id, _external=True),
    }
    return json_event


class EventAPI(Resource):
    @marshal_with(event_fields)
    def get(self, event_id):
        event = ListEvent.query.get_or_404(event_id)
        return jsonify_event(event)

restful_api.add_resource(EventAPI, '/events/<int:event_id>', endpoint='EventAPI')


'''
@api2.route('/events/<int:event_id>')
def get_event(event_id):
    event = ListEvent.query.get_or_404(event_id)
    return jsonify(event.to_json())
'''


@api2.route('/todo_lists/<int:list_id>/events/')
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
