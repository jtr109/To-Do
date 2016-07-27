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