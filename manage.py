#!/usr/bin/python

import os
from flask.ext.script import Manager, Shell

from app import create_app, db
from app.models import Role, User

app = create_app(os.getenv('TODO_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
