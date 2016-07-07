from flask import render_template, session, redirect, url_for, flash

from . import main
from .forms import NameForm
from ..models import User
from .. import db


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data)
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))

        # old_name = session.get('name')
        # if old_name is not None and old_name != form.name.data:
        #     flash('Looks like you have changed your name!')
        # session['name'] = form.name.data
        # return redirect(url_for('.index'))

    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))


@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

