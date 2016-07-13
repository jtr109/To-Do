from flask import render_template, url_for, redirect, flash
from flask_login import login_required, current_user

from . import main
from .forms import AddListForm, AddTaskForm
from ..models import User, ToDoList, Task, ListEvent
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
        event = ListEvent(event='Creat list: "%s".' % form.title.data,
                          list_id=todo_list.id)
        db.session.add(event)
        return redirect(url_for('.todo_list_details', list_id=todo_list.id))
    return render_template('index.html', form=form)


@main.route('/list/<int:list_id>', methods=['GET', 'POST'])
@login_required
def todo_list_details(list_id):
    current_list = ToDoList.query.filter_by(id=list_id).first()
    if current_user != current_list.master:
        flash("You can not view this page.")
        return redirect(url_for('.index'))
    form = AddTaskForm()
    if form.validate_on_submit():
        task = Task(body=form.task.data,
                    in_list=current_list)
        db.session.add(task)
        return redirect(url_for('.todo_list_details', list_id=list_id))
    todo_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='todo')
    doing_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='doing')
    done_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='done')
    return render_template('edit_list.html', current_list=current_list, form=form,
                           todo_tasks=todo_tasks, doing_tasks=doing_tasks, done_tasks=done_tasks)


@main.route('/task/delete_list/<int:list_id>')
@login_required
def delete_todo_list(list_id):
    todo_list = ToDoList.query.filter_by(id=list_id).first()
    todo_list.delete_todo_list()
    return redirect(url_for('.index', list_id=todo_list.id))


@main.route('/task/change_to_todo/<int:task_id>')
@login_required
def change_to_todo(task_id):
    task = Task.query.filter_by(id=task_id).first()
    original_state = task.state
    task.change_into_todo()
    event = ListEvent(event='Change "%s" from "%s" to "to do".' % (task.body, original_state),
                      list_id=task.list_id)
    db.session.add(event)
    return redirect(url_for('.todo_list_details', list_id=task.list_id))


@main.route('/task/change_to_doing/<int:task_id>')
@login_required
def change_to_doing(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.change_into_doing()
    return redirect(url_for('.todo_list_details', list_id=task.list_id))


@main.route('/task/change_to_done/<int:task_id>')
@login_required
def change_to_done(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.change_into_done()
    return redirect(url_for('.todo_list_details', list_id=task.list_id))


@main.route('/task/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.delete_task()
    return redirect(url_for('.todo_list_details', list_id=task.list_id))




