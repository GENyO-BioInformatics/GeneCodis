from requests import put, get, delete, post
import json

get('http://localhost:5000/todos/todo3').json()
delete('http://localhost:5000/todos/todo1')
post('http://localhost:5000/todos', data={"task":"ooo"})
put('http://localhost:5000/todos/todo3', data={"task":"something different"})
