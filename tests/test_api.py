import json
import random
import string

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


async def test_authors_creation_and_fetch(sanic_tester: SanicTestClient):
    name = ''.join([random.choice(string.ascii_lowercase) for i in range(16)])
    response = await sanic_tester.post("/authors", data=json.dumps({'name': name}))
    resp_json = await response.json()
    author = await sanic_tester.get("/authors/{}".format(resp_json['id']))
    author_json = await author.json()
    assert author_json['result']['name'] == name


async def test_authors_book_count(sanic_tester: SanicTestClient):
    book_count = {
            1: 2, 2: 2, 3: 2,
            4: 1, 5: 1, 6: 1,
            7: 1, 8: 2, 9: 1,
            10: 1, 11: 2, 12: 2
    }
    for i in book_count:
        response = await sanic_tester.get('/authors/relcount/{}'.format(str(i)))
        resp_json = await response.json()
        assert resp_json['result'] == book_count[i]


async def test_authors_fetch_books(sanic_tester: SanicTestClient):
    author_ids = {2: {1, 7}, 8: {4, 5}, 12: {9, 10}}
    for i in author_ids:
        response = await sanic_tester.get('/authors/rellist/{}'.format(str(i)))
        resp_json = await response.json()
        assert {b['id'] for b in resp_json['result']} == author_ids[i]


async def test_authors_m2m_idempotency(sanic_tester: SanicTestClient):
    response = None
    for i in range(3):
        response = await sanic_tester.put('/authors/1', data=json.dumps({'book_id': 4}))
    book_response = await sanic_tester.get('/books/relcount/4')
    gof_authors = await book_response.json()
    assert response.status == 304
    assert gof_authors['result'] == 5


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


async def test_books_creation_and_fetch(sanic_tester: SanicTestClient):
    name = ''.join([random.choice(string.ascii_lowercase) for i in range(16)])
    response = await sanic_tester.post("/books", data=json.dumps({'name': name}))
    resp_json = await response.json()
    book = await sanic_tester.get("/books/{}".format(resp_json['id']))
    book_json = await book.json()
    assert book_json['result']['name'] == name


async def test_books_author_count(sanic_tester: SanicTestClient):
    author_count = {
            1: 2, 2: 2, 3: 2, 4: 4, 5: 1,
            6: 1, 7: 2, 8: 1, 9: 2, 10: 1
    }
    for i in author_count:
        response = await sanic_tester.get('/books/relcount/{}'.format(str(i)))
        resp_json = await response.json()
        assert resp_json['result'] == author_count[i]


async def test_books_fetch_authors(sanic_tester: SanicTestClient):
    book_ids = {4: {5, 6, 7, 8}, 7: {2, 10}, 10: {12}}
    for i in book_ids:
        response = await sanic_tester.get('/books/rellist/{}'.format(str(i)))
        resp_json = await response.json()
        assert {a['id'] for a in resp_json['result']} == book_ids[i]


async def test_books_m2m_idempotency(sanic_tester: SanicTestClient):
    response = None
    for i in range(3):
        response = await sanic_tester.put('/books/10', data=json.dumps({'author_id': 4}))
    author_response = await sanic_tester.get('/authors/relcount/4')
    author_books = await author_response.json()
    assert response.status == 304
    assert author_books['result'] == 2

