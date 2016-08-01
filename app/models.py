from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from datetime import datetime

from . import db
from . import login_manager
from .exceptions import ValidationError


class Permission:
    NORMAL = 0x01
    MODERATE_LIST = 0x10
    REMOVE_LIST = 0x20
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.NORMAL,
                     True),
            'Administrator': (0xff, False),
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    todo_lists = db.relationship('ToDoList', backref='master', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['TODO_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_password_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset_password': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset_password') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_changing_email_request(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', user_id=self.id, _external=True),
            'username': self.username,
            'todo_lists': url_for('api.get_todo_lists', _external=True),
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class ToDoList(db.Model):
    __tablename__ = 'todo-lists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    master_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tasks = db.relationship('Task', backref='in_list', lazy='dynamic')
    events = db.relationship('ListEvent', backref='in_list', lazy='dynamic')

    @staticmethod
    def on_insert(mapper, connection, target):
        list_event = ListEvent(event='List "%s" was created.' % target.title,
                               list_id=target.id)
        db.session.add(list_event)

    @staticmethod
    def on_delete(mapper, connection, target):
        list_tasks = Task.query.filter_by(list_id=target.id)
        for t in list_tasks:
            db.session.delete(t)
        list_events = ListEvent.query.filter_by(list_id=target.id)
        for e in list_events:
            db.session.delete(e)

    def to_json(self):
        json_todo_list = {
            'url': url_for('api.get_todo_list', list_id=self.id, _external=True),
            'title': self.title,
            'timestamp': self.timestamp,
            'master': url_for('api.get_user', user_id=self.master_id, _external=True),
            'tasks': url_for('api.get_todo_list_tasks', list_id=self.id, _external=True),
            'events': url_for('api.get_todo_list_events', list_id=self.id, _external=True),
        }
        return json_todo_list

    @staticmethod
    def from_json(json_todo_list):
        title = json_todo_list.get('title')
        if title is None or title == '':
            raise ValidationError('todo list does not have a title')
        return ToDoList(title=title)

    def __repr__(self):
        return '<ToDoList %r>' % self.id

db.event.listen(ToDoList, 'after_insert', ToDoList.on_insert)
db.event.listen(ToDoList, 'before_delete', ToDoList.on_delete)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(64))
    state = db.Column(db.String(64), default='todo')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    list_id = db.Column(db.Integer, db.ForeignKey('todo-lists.id'))

    @staticmethod
    def on_changed_state(target, value, oldvalue, initiator):
        target.timestamp = datetime.utcnow()
        list_event = ListEvent(event='Task "%s" was changed from "%s" to "%s".' % (target.body, oldvalue, value),
                               list_id=target.list_id)
        db.session.add(list_event)

    @staticmethod
    def on_insert(mapper, connection, target):
        list_event = ListEvent(event='Task "%s" was created.' % target.body,
                               list_id=target.list_id)
        db.session.add(list_event)

    @staticmethod
    def on_delete(mapper, connection, target):
        list_event = ListEvent(event='Task "%s" was deleted.' % target.body,
                               list_id=target.list_id)
        db.session.add(list_event)

    def to_json(self):
        json_task = {
            'url': url_for('api.get_task', task_id=self.id, _external=True),
            'body': self.body,
            'state': self.state,
            'timestamp': self.timestamp,
            'todo_list': url_for('api.get_todo_list', list_id=self.list_id, _external=True),
        }
        return json_task

    @staticmethod
    def from_json(json_todo_list):
        body = json_todo_list.get('body')
        if body is None or body == '':
            raise ValidationError('todo list does not have a title')
        return Task(body=body)

    def __repr__(self):
        return '<Task %r>' % self.id

db.event.listen(Task.state, 'set', Task.on_changed_state)
db.event.listen(Task, 'after_insert', Task.on_insert)
db.event.listen(Task, 'before_delete', Task.on_delete)


class ListEvent(db.Model):
    __tablename__ = 'list-events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    list_id = db.Column(db.Integer, db.ForeignKey('todo-lists.id'))

    def to_json(self):
        json_list_event = {
            'url': url_for('api.get_event', event_id=self.id, _external=True),
            'event': self.event,
            'timestamp': self.timestamp,
            'todo_list': url_for('api.get_todo_list', list_id=self.list_id, _external=True),
        }
        return json_list_event

    def __repr__(self):
        return '<List Event %r>' % self.id
