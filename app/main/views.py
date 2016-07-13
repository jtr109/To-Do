from flask import render_template, url_for, redirect, flash
from flask_login import login_required, current_user

from . import main
from .forms import AddListForm, AddTaskForm, \
    ChangeToTodoForm, ChangeToDoingForm, ChangeToDoneForm, DeleteTaskForm
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
        todo_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='todo')
        doing_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='doing')
        done_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='done')
    else:
        flash("You can not view this page.")
        return redirect(url_for('main.index'))
    return render_template('edit_list.html', title=current_list.title, form=form,
                           todo_tasks=todo_tasks, doing_tasks=doing_tasks, done_tasks=done_tasks)


@main.route('/task/change_to_todo/<int:task_id>')
@login_required
def change_to_todo(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.change_into_todo()
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




