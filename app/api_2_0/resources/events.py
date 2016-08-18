from flask import request, g, url_for, current_app
# flask-restful
from flask_restful import Resource, fields, marshal_with
from app import restful_api

from ...models import ListEvent, ToDoList
from .errors import unauthorized

event_fields = {
    'url': fields.String,
    'event': fields.String,
    'timestamp': fields.DateTime(dt_format='rfc822'),
    'todo_list': fields.String,
}

events_fields = {
    'events': fields.Nested(event_fields),
    'prev': fields.String,
    'next': fields.String,
    'count': fields.Integer,
}


def to_json_event(event):
    json_event = {
        'url': url_for('api2.EventAPI', event_id=event.id, _external=True),
        'event': event.event,
        'timestamp': event.timestamp,
        'todo_list': url_for('api2.TodoListAPI', list_id=event.list_id, _external=True),
    }
    return json_event


class EventAPI(Resource):
    @marshal_with(event_fields)
    def get(self, event_id):
        event = ListEvent.query.get_or_404(event_id)
        if event.in_list.master != g.current_user:
            return unauthorized("Invalid master!")
        return to_json_event(event)

restful_api.add_resource(EventAPI, '/events/<int:event_id>', endpoint='EventAPI')


class EventsAPI(Resource):
    @marshal_with(events_fields)
    def get(self, list_id):
        todo_list = ToDoList.query.get_or_404(list_id)
        if todo_list.master != g.current_user:
            return unauthorized("Invalid User.")
        page = request.args.get('page', 1, type=int)
        pagination = ListEvent.query.filter_by(list_id=list_id). \
            order_by(ListEvent.timestamp.desc()).paginate(
            page, per_page=current_app.config['TODO_POSTS_PER_PAGE'],
            error_out=False)
        events = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api2.EventsAPI', list_id=list_id, page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api2.EventsAPI', list_id=list_id, page=page+1, _external=True)
        return {
            'events': [to_json_event(event) for event in events],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }

restful_api.add_resource(EventsAPI, '/todo-lists/<int:list_id>/events/', endpoint='EventsAPI')
