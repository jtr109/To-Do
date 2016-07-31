# ToDo

Homepage: [click here](https://jtr-todo.herokuapp.com/)

## 角色权限

### 程序权限

操作                         |位值                 |说明
:---------------------------|:-------------------|:----------------------------------
NORMAL                      |0b00000001 (0x01)   |view and edit your private list
MODERATE_LIST               |0b00010000 (0x10)   |view and user's list
REMOVE_LIST                 |0b00100000 (0x20)   |remove user's list
ADMINISTOR                  |0b10000000 (0x80)   |admin web

### 用户角色

用户角色|权限|说明
:-|:-|:-
匿名|0b00000000 (0x00)|未登录用户
用户|0b00000001 (0x01)|创建和编辑list
协管员|0b00111111 (0x3f)|增加审查和删除他人list的权限
管理员|0b11111111 (0xff)|所有权限，包括修改其他用户所属权限


## API Documents

### `GET` /api/v1.0/token

#### Implementation Notes

get token

#### Response Class (Status 200)

OK

Model | Model schema

    {
        "expiration": 3600,
        "token":eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ2OTg3MjY1NywiaWF0IjoxNDY5ODY5MDU3fQ.eyJpZCI6MX0.qDMfoALz│42SVVCulUyedjf2pR1KEgM8i7DZ-QrZqefl3M",
        "user_id": 1,
    }

Response Content Type: json

#### Parameters

Parameter      | Desciption        | Parameter Type | Data Type
:--------------|:------------------|:---------------|:--------------
param.email    | The email of user | header         | string
param.password | The password      | header         | string

### `GET` /api/v1.0/users/{int:user_id}

#### Implementation Notes

Get information about user

#### Response Class (Status 200)

OK

Model | Model schema

    {
        "todo_lists": "http://127.0.0.1:5000/api/v1.0/todo_lists/",
        "url": "http://127.0.0.1:5000/api/v1.0/users/1",
        'username": "user1",
    }

Response Content Type: json

#### Parameters

Parameter            | Desciption                            | Parameter Type | Data Type
:--------------------|:--------------------------------------|:---------------|:--------------
param.email_or_token | The email or token of user            | header         | string
param.password       | The password or None if token is used | header         | string

### `GET` /api/v1.0/todo_lists/

#### Implementation Notes

Get a list of todo_lists of current user

#### Response Class (Status 200)

OK

Model | Model schema

{
    "count": 2,
    "next": null,
    "prev": null,
    "todo_lists": [
        {
            "events": "http://127.0.0.1:5000/api/v1.0/todo_lists/1/events/",
            "master": "http://127.0.0.1:5000/api/v1.0/users/1",
            "tasks": "http://127.0.0.1:5000/api/v1.0/todo_lists/1/tasks/",
            "timestamp": "Fri, 29 Jul 2016 08:03:23 GMT",
            "title": "First list by api",
            "url": "http://127.0.0.1:5000/api/v1.0/todo_lists/1"
        },
        {
            "events": "http://127.0.0.1:5000/api/v1.0/todo_lists/3/events/",
            "master": "http://127.0.0.1:5000/api/v1.0/users/1",
            "tasks": "http://127.0.0.1:5000/api/v1.0/todo_lists/3/tasks/",
            "timestamp": "Fri, 29 Jul 2016 08:03:23 GMT",
            "title": "First list by api",
            "url": "http://127.0.0.1:5000/api/v1.0/todo_lists/3"
        },
    ]
}

Response Content Type: json

#### Parameters

Parameter            | Desciption                            | Parameter Type | Data Type
:--------------------|:--------------------------------------|:---------------|:--------------
param.email_or_token | The email or token of user            | header         | string
param.password       | The password or None if token is used | header         | string

### `POST` /api/v1.0/todo_lists/

#### Implementation Notes

Create a new todo list

#### Response Class (Status 201)

OK

Model | Model schema

{
    "events": "http://127.0.0.1:5000/api/v1.0/todo_lists/4/events/",
    "master": "http://127.0.0.1:5000/api/v1.0/users/1",
    "tasks": "http://127.0.0.1:5000/api/v1.0/todo_lists/4/tasks/",
    "timestamp": "Sun, 31 Jul 2016 06:17:54 GMT",
    "title": "new list",
    "url": "http://127.0.0.1:5000/api/v1.0/todo_lists/4"
}

Response Content Type: json

#### Parameters

Parameter            | Value      | Desciption                            | Parameter Type | Data Type
:--------------------|:-----------|:--------------------------------------|:---------------|:--------------
param.email_or_token |            | The email or token of user            | header         | string
param.password       |            | The password or None if token is used | header         | string
param.title          | 'new list' | The title of new list                 | query          | string

### `GET` /api/v1.0/todo_lists/{int:list_id}

#### Implementation Notes

Get infomations about the todo list

#### Response Class (Status 200)

OK

Model | Model schema

{
    "events": "http://127.0.0.1:5000/api/v1.0/todo_lists/5/events/",
    "master": "http://127.0.0.1:5000/api/v1.0/users/1",
    "tasks": "http://127.0.0.1:5000/api/v1.0/todo_lists/5/tasks/",
    "timestamp": "Sun, 31 Jul 2016 06:29:19 GMT",
    "title": "new task with json",
    "url": "http://127.0.0.1:5000/api/v1.0/todo_lists/5"
}


Response Content Type: json

#### Parameters

Parameter            | Value      | Desciption                            | Parameter Type | Data Type
:--------------------|:-----------|:--------------------------------------|:---------------|:--------------
param.email_or_token |            | The email or token of user            | header         | string
param.password       |            | The password or None if token is used | header         | string

### `DELETE` /api/v1.0/todo_lists/{int:list_id}

#### Implementation Notes

Delete a todo list

#### Response Class (Status 303)

OK

Model | Model schema

{
    "Location": "http://127.0.0.1:5000/api/v1.0/todo_lists/"
}


Response Content Type: json

#### Parameters

Parameter            | Value      | Desciption                            | Parameter Type | Data Type
:--------------------|:-----------|:--------------------------------------|:---------------|:--------------
param.email_or_token |            | The email or token of user            | header         | string
param.password       |            | The password or None if token is used | header         | string


### `POST` /api/v1.0/todo_lists/5/tasks/

#### Implementation Notes

Add new task into the todo list

#### Response Class (Status 201)

OK

Model | Model schema

{
    "body": "first task",
    "state": "todo",
    "timestamp": "Sun, 31 Jul 2016 10:52:41 GMT",
    "todo_list": "http://127.0.0.1:5000/api/v1.0/todo_lists/5",
    "url": "http://127.0.0.1:5000/api/v1.0/tasks/2"
}


Response Content Type: json

Response Location: http://127.0.0.1:5000/api/v1.0/todo_lists/5/tasks/

#### Parameters

Parameter            | Value      | Desciption                            | Parameter Type | Data Type
:--------------------|:-----------|:--------------------------------------|:---------------|:--------------
param.email_or_token |            | The email or token of user            | header         | string
param.password       |            | The password or None if token is used | header         | string
param.body           | 'new task' | The body of new task                  | query          | string


### `GET` /api/v1.0/todo_lists/5/tasks/

#### Implementation Notes

Show all tasks in the list

#### Response Class (Status 200)

OK

Model | Model schema

{
    "doing_tasks": [],
    "done_tasks": [],
    "todo_tasks": [
        {
            "body": "first task",
            "state": "todo",
            "timestamp": "Sun, 31 Jul 2016 10:52:41 GMT",
            "todo_list": "http://127.0.0.1:5000/api/v1.0/todo_lists/5",
            "url": "http://127.0.0.1:5000/api/v1.0/tasks/2"
        },
        {
            "body": "second task",
            "state": "todo",
            "timestamp": "Sun, 31 Jul 2016 11:04:56 GMT",
            "todo_list": "http://127.0.0.1:5000/api/v1.0/todo_lists/5",
            "url": "http://127.0.0.1:5000/api/v1.0/tasks/3"
        }
    ]
}


Response Content Type: json

#### Parameters

Parameter            | Desciption                            | Parameter Type | Data Type
:--------------------|:--------------------------------------|:---------------|:--------------
param.email_or_token | The email or token of user            | header         | string
param.password       | The password or None if token is used | header         | string

### `GET` /api/v1.0/tasks/{int:task_id}

#### Implementation Notes

Get details of the task

#### Response Class (Status 200)

OK

Model | Model schema

{
    "body": "first task",
    "state": "todo",
    "timestamp": "Sun, 31 Jul 2016 10:52:41 GMT",
    "todo_list": "http://127.0.0.1:5000/api/v1.0/todo_lists/5",
    "url": "http://127.0.0.1:5000/api/v1.0/tasks/2"
}

Response Content Type: json

#### Parameters

Parameter            | Desciption                            | Parameter Type | Data Type
:--------------------|:--------------------------------------|:---------------|:--------------
param.email_or_token | The email or token of user            | header         | string
param.password       | The password or None if token is used | header         | string

### `PATCH` /api/v1.0/tasks/{int:task_id}

#### Implementation Notes

Change state of the task

#### Response Class (Status 202)

OK

Model | Model schema

{
    "body": "first new test task after fix bug",
    "state": "doing",
    "timestamp": "Sun, 31 Jul 2016 12:48:31 GMT",
    "todo_list": "http://127.0.0.1:5000/api/v1.0/todo_lists/7",
    "url": "http://127.0.0.1:5000/api/v1.0/tasks/5"
}

Response Content Type: json

#### Parameters

Parameter            | Desciption                            | Parameter Type | Data Type
:--------------------|:--------------------------------------|:---------------|:--------------
param.email_or_token | The email or token of user            | header         | string
param.password       | The password or None if token is used | header         | string
param.state          | The new state of the task             | query          | string

### `DELETE` /api/v1.0/tasks/{int:task_id}

#### Implementation Notes

delete the task

#### Response Class (Status 303)

OK

Model | Model schema

null

Response Content Type: json

#### Parameters

Parameter            | Desciption                            | Parameter Type | Data Type
:--------------------|:--------------------------------------|:---------------|:--------------
param.email_or_token | The email or token of user            | header         | string
param.password       | The password or None if token is used | header         | string
