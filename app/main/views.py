from flask import render_template, url_for, redirect, flash, request, abort
from flask_login import login_required, current_user, current_app

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
        return redirect(url_for('.todo_list_details', list_id=todo_list.id))
    page = request.args.get('page', 1, type=int)
    pagination = ToDoList.query.order_by(ToDoList.timestamp.desc()).filter_by(master=current_user).paginate(
        page, per_page=current_app.config['TODO_POSTS_PER_PAGE'], error_out=False)
    todo_lists = pagination.items
    return render_template('index.html', form=form,
                           pagination=pagination, todo_lists=todo_lists)


@main.route('/list/<int:list_id>', methods=['GET', 'POST'])
@login_required
def todo_list_details(list_id):
    current_list = ToDoList.query.filter_by(id=list_id).first_or_404()
    if current_user != current_list.master:
        flash("You can not view this page.")
        abort(403)
    form = AddTaskForm()
    if form.validate_on_submit():
        task = Task(body=form.task.data,
                    list_id=list_id)
        db.session.add(task)
        return redirect(url_for('.todo_list_details', list_id=list_id))
    todo_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='todo')
    doing_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='doing')
    done_tasks = Task.query.order_by(Task.timestamp.desc()).filter_by(list_id=list_id, state='done')
    page = request.args.get('page', 1, type=int)
    pagination = ListEvent.query.order_by(ListEvent.timestamp.desc()).filter_by(list_id=list_id).paginate(
        page, per_page=current_app.config['TODO_POSTS_PER_PAGE'], error_out=False)
    list_events = pagination.items
    return render_template('edit_list.html', current_list=current_list, form=form,
                           todo_tasks=todo_tasks, doing_tasks=doing_tasks, done_tasks=done_tasks,
                           pagination=pagination, list_events=list_events)


@main.route('/task/delete_list/<int:list_id>')
@login_required
def delete_todo_list(list_id):
    todo_list = ToDoList.query.filter_by(id=list_id).first_or_404()
    if current_user != todo_list.master:
        abort(403)
    db.session.delete(todo_list)
    return redirect(url_for('.index', list_id=todo_list.id))


@main.route('/task/change_to_todo/<int:task_id>')
@login_required
def change_to_todo(task_id):
    task = Task.query.filter_by(id=task_id).first_or_404()
    if current_user != task.in_list.master:
        abort(403)
    task.state = 'todo'
    return redirect(url_for('.todo_list_details', list_id=task.list_id))


@main.route('/task/change_to_doing/<int:task_id>')
@login_required
def change_to_doing(task_id):
    task = Task.query.filter_by(id=task_id).first_or_404()
    if current_user != task.in_list.master:
        abort(403)
    task.state = 'doing'
    return redirect(url_for('.todo_list_details', list_id=task.list_id))


@main.route('/task/change_to_done/<int:task_id>')
@login_required
def change_to_done(task_id):
    task = Task.query.filter_by(id=task_id).first_or_404()
    if current_user != task.in_list.master:
        abort(403)
    task.state = 'done'
    return redirect(url_for('.todo_list_details', list_id=task.list_id))


@main.route('/task/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first_or_404()
    if current_user != task.in_list.master:
        abort(403)
    db.session.delete(task)
    return redirect(url_for('.todo_list_details', list_id=task.list_id))




