# Sanic + SQLAlchemy CRUD

The project is based on [this](https://github.com/harshanarayana/cookiecutter-sanic) cookiecutter.

### Getting started
One line with `docker-compose`:
```
$ docker-compose build
```
And you are ready to go:
```
$ docker-compose up
```
Beware that the **DB is dropped** and the **initial data is loaded on Sanic start**. Contact me if you would like to have this behavior amended.

If you have PostgreSQL running system-wide you will need to stop the service.

### Testing
While the docker is up:
```
$ docker exec -it <sanic_bookstore_1> pytest tests/ 
```

#### Simple GUI:
http://127.0.0.1:8080

As long as I claimed to be a full stack dev I have suppplied the project with a simple Vue.js GUI CRUD. 
It is NOT intended to be even close to production-ready, this would require general server API redesign. 
It is just here to facilitate the checking of the task and to show some basics I can do with it.

##### Interactive docs:
http://127.0.0.1:8000/swagger



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
curl -X PATCH "http://127.0.0.1:8000/authors/1" -H "accept --data '{"name": "D. R."}'
```
or
```
curl -X PUT "http://127.0.0.1:8000/authors/1" -H "accept --data '{"name": "D. R."}'
```

Books:
```
curl -X PATCH "http://127.0.0.1:8000/books/1" -H "accept --data '{"name": "K&R"}'
```
or
```
curl -X PUT "http://127.0.0.1:8000/authors/1" -H "accept --data '{"name": "K&R"}'
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
curl -X GET "http://127.0.0.1:8000/authors/rellist/1" -H "accept: application/json"
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



