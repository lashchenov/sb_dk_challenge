import json

from sanic.testing import SanicTestClient


async def test_authors(sanic_tester: SanicTestClient):
    response = await sanic_tester.get("/authors")
    resp_json = await response.json()
    assert response.status == 200
    assert len(resp_json['result']) == 12


async def test_authors_loaded_first(sanic_tester: SanicTestClient):
    response = await sanic_tester.get("/authors/1")
    resp_json = await response.json()
    assert resp_json['result']['name'] == 'Dennis Ritchie'


async def test_authors_loaded_last(sanic_tester: SanicTestClient):
    response = await sanic_tester.get("/authors/12")
    resp_json = await response.json()
    assert resp_json['result']['name'] == 'C.A.R. Hoare'


async def test_authors_creation(sanic_tester: SanicTestClient):
    response = await sanic_tester.post("/authors", data=json.dumps({'name': 'Test Author'}))
    resp_json = await response.json()
    assert response.status == 201
    assert resp_json['id'] == 13


async def test_nonexisting_authors_update(sanic_tester: SanicTestClient):
    response = await sanic_tester.put("/authors/321", data=json.dumps({'name': 'Test'}))
    assert response.status == 404


async def test_nonexisting_authors_deletion(sanic_tester: SanicTestClient):
    response = await sanic_tester.delete("/authors/123")
    assert response.status == 404


async def test_books(sanic_tester: SanicTestClient):
    response = await sanic_tester.get("/books")
    resp_json = await response.json()
    assert response.status == 200
    assert len(resp_json['result']) == 10


async def test_books_loaded_first(sanic_tester: SanicTestClient):
    response = await sanic_tester.get("/books/1")
    resp_json = await response.json()
    assert resp_json['result']['name'] == 'The C Programming Language'


async def test_books_loaded_last(sanic_tester: SanicTestClient):
    response = await sanic_tester.get("/books/10")
    resp_json = await response.json()
    assert resp_json['result']['name'] == 'Communicating Sequential Processes'


async def test_book_creation(sanic_tester: SanicTestClient):
    response = await sanic_tester.post("/books", data=json.dumps({'name': 'Test Book'}))
    resp_json = await response.json()
    assert response.status == 201
    assert resp_json['id'] == 11


async def test_nonexisting_books_update(sanic_tester: SanicTestClient):
    response = await sanic_tester.put("/books/321", data=json.dumps({'name': 'Test'}))
    assert response.status == 404


async def test_nonexisting_books_deletion(sanic_tester: SanicTestClient):
    response = await sanic_tester.delete("/books/123")
    assert response.status == 404

