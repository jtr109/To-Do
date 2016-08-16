import unittest
from api_app import db, create_app
from api_app.models import ToDoList, Task, ListEvent


class ListEventTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_list_event(self):
        todo_list = ToDoList(title='test')
        db.session.add(todo_list)
        db.session.commit()
        events = ListEvent.query.filter_by(in_list=todo_list).all()
        self.assertTrue(len(events) == 1)
        e1 = events[0]
        self.assertTrue(e1.event == 'List "test" was created.')

    def test_delete_list_event(self):
        todo_list = ToDoList(title='test')
        db.session.add(todo_list)
        db.session.commit()
        events1 = ListEvent.query.filter_by(in_list=todo_list).all()
        self.assertFalse(events1 == [])
        list_id = todo_list.id
        db.session.delete(todo_list)
        db.session.commit()
        events2 = ListEvent.query.filter_by(list_id=list_id).all()
        self.assertTrue(events2 == [])

    def test_record_creation_and_delete_of_task(self):
        todo_list = ToDoList(title='test list')
        db.session.add(todo_list)
        db.session.commit()
        task1 = Task(body='task1', in_list=todo_list)
        db.session.add(task1)
        db.session.commit()
        event1 = ListEvent.query.filter_by(event='Task "task1" was created.',
                                           in_list=todo_list).all()
        # the only event of task1 was created
        self.assertEqual(len(event1), 1)
        db.session.delete(task1)
        db.session.commit()
        event2 = ListEvent.query.filter_by(event='Task "task1" was deleted.',
                                           in_list=todo_list).all()
        # the only event of task1 was deleted
        self.assertEqual(len(event2), 1)

    def test_state_changes_of_task(self):
        todo_list = ToDoList(title='test list')
        db.session.add(todo_list)
        db.session.commit()
        task1 = Task(body='task1', in_list=todo_list)
        db.session.add(task1)
        db.session.commit()
        # default state of task is 'to do'
        self.assertTrue(task1.state == 'todo')
        timestamp1 = task1.timestamp
        task1.state = 'doing'
        db.session.add(task1)
        db.session.commit()
        # timestamp of task was changed
        self.assertNotEqual(timestamp1, task1.timestamp)
        event1 = ListEvent.query.filter_by(event='Task "task1" was changed from "todo" to "doing".',
                                           in_list=todo_list).all()
        # the only event of task1 was changed
        self.assertEqual(len(event1), 1)



