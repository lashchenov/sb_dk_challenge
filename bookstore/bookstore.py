import os
import json
import asyncio
import datetime

import uvloop
import asyncpgsa

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

from aiopg.sa import create_engine

from psycopg2 import IntegrityError

from sanic import Sanic
from sanic.response import json as jsonify
from sanic_openapi import swagger_blueprint, openapi_blueprint, doc
from bookstore.blueprint.health import health

# db_user = 'postgres'
db_user = db_host = os.environ['SANIC_DB_HOST']
db_name = os.environ['SANIC_DB_DATABASE']
db_password = os.environ['SANIC_DB_PASSWORD']

connection = 'postgres://{u}:{up}@{h}/{hp}'.format(u=db_user, up=db_password, h=db_host, hp=db_name)

metadata = sa.MetaData()
Base = declarative_base()
Session = sessionmaker()
session = Session()


mapping_table = sa.Table(
                'author_book_rel', metadata,
                sa.Column('author_id', sa.Integer, sa.ForeignKey('authors_table.id')),
                sa.Column('book_id', sa.Integer, sa.ForeignKey('books_table.id')),
             )

authors_table = sa.Table(
                'author', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('name', sa.String(32)),
             )

books_table = sa.Table(
                'book', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('name', sa.String(128)),
             )


app = Sanic(__name__)


app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)

app.blueprint(health)


def cors(fn):
    """A very simple decorator to add CORS headers
    for the local front without external plugins
    """
    async def wrapper(*args, **kwargs):
        response = await fn(*args, **kwargs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Max-Age'] = '1200'
        return response
    return wrapper


class CRUDFactory:
    """As long as both tables have the same column set
    it is possible to design a universal CRUD factory.
    :table: sqlalchemy.schema.Table 
    :slug: an acceptable by sanic.route('/path') decorator
    Sanic instance should be declared globally.
    """
    def __init__(self, table, slug, related=False):
        self.table = table
        self.slug = slug

        self.related = related

        app.route(slug, methods=["POST"])(self.create)
        doc.summary('Creates a record by name, assigns sequential ID.')(self.create)
        doc.consumes({"name": str})

        app.route(os.path.join(slug, '<db_id:int>'), methods=["GET",])(self.read)
        doc.summary('Fetches a single record by ID or all at once')(self.read)
        doc.produces({"result": {"id": int, "name": str}})(self.read)

        app.route(slug, methods=["GET"])(self.read)

        app.route(os.path.join(slug, '<db_id:int>'), methods=["PUT", "PATCH"])(self.update)
        app.route(os.path.join(slug, '<db_id:int>'), methods=["OPTIONS"])(self.preflight)
        doc.summary('Updates a record by ID.')(self.update)
        doc.consumes({"name": str, "author_id/book_id": int, "id": int})(self.update)

        app.route(os.path.join(slug, '<db_id:int>'), methods=["DELETE"])(self.delete)
        doc.summary('Deletes a record by ID.')(self.delete)
        doc.produces({"result": "Success"})(self.delete)

        app.route(os.path.join(slug, 'relcount', '<db_id:int>'), methods=["GET"])(self.count_related)
        doc.summary('Counts related authors/books by ID.')(self.count_related)
        doc.produces({"result": int})(self.count_related)

        app.route(os.path.join(slug, 'rellist', '<db_id:int>'), methods=["GET"])(self.list_related)
        doc.summary('Lists related authors/books by ID.')(self.list_related)
        doc.produces({"result": [{"id": int, "name": str}]})


    @cors
    async def preflight(self, *args, **kwargs):
        return jsonify({'message': 'A workaround for browsers'})

    @cors
    async def create(self, request):
        # async with create_engine(connection) as engine:
        async with app.pool.acquire() as conn:
            result = await conn.execute(self.table.insert().values(name=request.json['name']))
            row = await result.fetchall() 
            try:
                return jsonify({'id': row[0]['id']}, status=201)
            except Exception as e:
                return jsonify({'error': str(e)})

    @cors
    async def read(self, request, db_id=False):
        # async with create_engine(connection) as engine:
        async with app.pool.acquire() as conn:
            print('AUTHORS COUNT:') 
            print(await conn.fetchval(sa.select([sa.func.count()]).select_from(self.table)))
            if not db_id:
                # rows = []
                # async for row in conn.execute(self.table.select()):
                #     rows.append({'id': row.id, 'name': row.name})
                result = [dict(r) for r in await conn.fetch(authors_table.select())]
                return jsonify({'result': result})    
            else:
                row = await conn.fetchrow(self.table.select(self.table.c.id == db_id))
                return jsonify({'result': dict(row)})
                # result = await row.fetchall()
                # try:
                #     row_id, name = result[0]['id'], result[0]['name']
                #     return jsonify({'result': {'id': row_id, 'name': name}})
                # except IndexError:
                #         return jsonify({'error': 'No matching record was found.'}, status=404)
    
    @cors
    async def update(self, request, db_id):
        # async with create_engine(connection) as engine:
        async with app.pool.acquire() as conn:
            try:
                modified = False
                columns = self.related.name.split('_')[:-1]
                related_name = [n for n in columns if n != self.table.name].pop()
                related_id = request.json.pop(related_name + '_id', None)
                if related_id:
                    modified = True
                    rel_cols = [c + '_id' for c in columns]
                    values = {self.table.name + '_id': db_id,
                              related_name + '_id': related_id}
                    await conn.execute(
                        """INSERT INTO {rel}
                               ({cols})
                           SELECT {vals}
                           WHERE
                               NOT EXISTS(
                                   SELECT {cols} FROM {rel} WHERE {fko} = {fkov} AND {fkt} = {fktv}
                               );
                        """.format(rel=self.related.name,
                            cols=', '.join(rel_cols),
                            vals=str(values[rel_cols[0]]) + ',' + str(values[rel_cols[1]]),
                            fko=rel_cols[0],
                            fkov=values[rel_cols[0]],
                            fkt=rel_cols[1],
                            fktv=values[rel_cols[1]])
                    )
                if request.json:
                    row = await conn.execute(
                        self.table.update().values(**request.json).where(self.table.c.id == db_id)
                    )
                    modified = modified or bool(row.rowcount)
                return jsonify(
                    {'result': 'Success' if modified else 'No matching record found.'},
                    status=200 if modified else 404
                )
            except IntegrityError:
                return jsonify({'error': 'Invalid ID supplied.'}, status=400)

    
    @cors
    async def delete(self, request, db_id):
    # async with create_engine(connection) as engine:
        async with app.pool.acquire() as conn:
            result = await conn.execute(self.table.delete().where(self.table.c.id == db_id))
            return jsonify(
                    {'result': 'Success' if result.rowcount else 'No matching record found.'},
                    status=200 if result.rowcount else 404
            )


    @cors
    async def count_related(self, request, db_id):
        # async with create_engine(connection) as engine:
        async with app.pool.acquire() as conn:
            rows = await conn.execute(
                    self.related.select().where(self.related.c[self.table.name + '_id'] == db_id)
            )
            result = rows.rowcount
            return jsonify({'result': result})


    @cors
    async def list_related(self, request, db_id):
        # async with create_engine(connection) as engine:
        async with app.pool.acquire() as conn:
            field_names = self.related.name.split('_')[:-1]
            field_names.remove(self.table.name)
            related_name = field_names.pop()
            query_args = {
                'rel': related_name,
                'map': self.related.name,
                'cur': self.table.name,
                'db_id': str(db_id) # no need to sanitize, the type is cast explicitly
            }
            rows = []
            # Quering by raw SQL here because I fucked it up during the interview
            # It is also far more expressive and readable than SQLAlchemy native 
            # method chaining
            async for row in conn.execute("""SELECT {rel}.id, {rel}.name
                                                 FROM {rel}
                                                 LEFT JOIN {map}
                                                        ON {rel}.id = {map}.{rel}_id
                                                 LEFT JOIN {cur} 
                                                        ON {cur}.id = {map}.{cur}_id
                                                 WHERE {cur}_id = {db_id}""".format(**query_args)):
                rows.append({'id': row.id, 'name': row.name})
            return jsonify({'result': rows})
                

CRUDFactory(authors_table, '/authors', related=mapping_table)
CRUDFactory(books_table, '/books', related=mapping_table)


@app.listener('before_server_start')
async def prepare_db(app, loop):
    app.pool = await asyncpgsa.create_pool(connection)
    async with app.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute('DROP TABLE IF EXISTS author_book_rel')
            await conn.execute('DROP TABLE IF EXISTS author')
            await conn.execute('DROP TABLE IF EXISTS book')
            await conn.execute("""CREATE TABLE author (
                                   id serial primary key,
                                   name varchar(32)
                               );
                               CREATE TABLE book (
                                   id serial primary key,
                                   name varchar(128)
                               );
                               CREATE TABLE author_book_rel (
                                   author_id INTEGER REFERENCES author(id)
                                             ON DELETE CASCADE ON UPDATE CASCADE,
                                   book_id INTEGER REFERENCES book(id) 
                                           ON DELETE CASCADE ON UPDATE CASCADE
                               );""")
            with open('bookstore/initial.json', 'r') as fixture:
                data = json.loads(fixture.read())
                authors, books, mapping = (data[k] for k in ['authors', 'books', 'map'])
                for author in authors:
                    await conn.execute(str(authors_table.insert().values(name=author).compile(compile_kwargs={"literal_binds": True})))
                for book in books:
                    await conn.execute(str(books_table.insert().values(name=book).compile(compile_kwargs={"literal_binds": True})))
                for i, link in enumerate(mapping):
                    for book in link:
                        await conn.execute(str(mapping_table.insert().values(author_id=i+1, book_id=book).compile(compile_kwargs={'literal_binds': True})))

