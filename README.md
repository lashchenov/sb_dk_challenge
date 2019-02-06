# Sanic + SQLAlchemy CRUD

The project is based on [this](https://github.com/harshanarayana/cookiecutter-sanic) cookiecutter.

### Create
Authors: 

```
curl -X POST "http://127.0.0.1:8000/authors/" -H  "accept: application/json" -H  "content-type: application/json" --data '{"name": "New Author"}'
```

Books:
```
curl -X POST "http://127.0.0.1:8000/books/" -H  "accept: application/json" -H  "content-type: application/json" --data '{"name": "New Book"}'
```

### Read
Authors:
```
curl -X GET "http://127.0.0.1:8000/authors" -H "accept: application/json"
```

Books:

```
curl -X GET "http://127.0.0.1:8000/authors" -H "accept: application/json"
```

### Update
Authors:
```
curl -X PATCH "http://127.0.0.1:8000/authors/1" -H "accep --data '{"name": "D. R."}'
```
or
```
curl -X PUT "http://127.0.0.1:8000/authors/1" -H "accep --data '{"name": "D. R."}'
```

Books:
```
curl -X PUT "http://127.0.0.1:8000/books/1" -H "accep --data '{"name": "K&R"}'
```
or
```
curl -X PUT "http://127.0.0.1:8000/authors/1" -H "accep --data '{"name": "K&R"}'
```

### Delete
Authors:
```
curl -X DELETE "http://127.0.0.1:8000/authors/2" -H  "accept: application/json" -H  "content-type: application/json"
```

Books:
```
curl -X DELETE "http://127.0.0.1:8000/books/4" -H  "accept: application/json" -H  "content-type: application/json"
```

### List related authors/books
Books of an author:
```
curl -X GET "http://127.0.0.1:8000/authors/rel/1" -H "accept: application/json"
```

Authors of a book:
```
curl -X GET "http://127.0.0.1:8000/books/rellist/4" -H "accept: application/json"
```


### Count related authors/books
Books of an author:
```
curl -X GET "http://127.0.0.1:8000/authors/relcount/1" -H "accept: application/json"
```

Authors of a book:
```
curl -X GET "http://127.0.0.1:8000/books/relcount/4" -H "accept: application/json"
```


##### Try it out interactively with a GUI:
http://127.0.0.1:8000/swagger
