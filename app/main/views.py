from flask import render_template, url_for, redirect, flash
from flask_login import login_required, current_user

from . import main
from .forms import AddListForm, AddTaskForm
from ..models import User, ToDoList, Task
from .. import db


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = AddListForm()
    if form.validate_on_submit():
        todo_list = ToDoList(title=form.title.data,
                        master=current_user._get_current_object())
        db.session.add(todo_list)
        db.session.commit()
        return redirect(url_for('.todo_list_details', list_id=todo_list.id))
    return render_template('index.html', form=form)


@main.route('/list/<int:list_id>', methods=['GET', 'POST'])
@login_required
def todo_list_details(list_id):
    current_list = ToDoList.query.filter_by(id=list_id).first()
    form = AddTaskForm()
    if form.validate_on_submit():
        task = Task(body=form.task.data,
                    in_list=current_list)
        db.session.add(task)
        return redirect(url_for('.todo_list_details', list_id=list_id))
    if current_user == current_list.master:
        to_do_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='todo')
    else:
        flash("You can not view this page.")
        return redirect(url_for('main.index'))
    return render_template('edit_list.html', title=current_list.title, to_do_tasks=to_do_tasks, form=form)



# todo: unfinished
