from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddListForm(Form):
    title = StringField('Add new List.', validators=[DataRequired()])
    submit = SubmitField('Add')


class AddTaskForm(Form):
    task = StringField('Add task.', validators=[DataRequired()])
    submit = SubmitField('Add')


class ChangeToTodoForm(Form):
    submit = SubmitField('Change to Todo')


class ChangeToDoingForm(Form):
    submit = SubmitField('Change to Doing')


class ChangeToDoneForm(Form):
    submit = SubmitField('Change to Done')


class DeleteTaskForm(Form):
    submit = SubmitField('Delete this task')
