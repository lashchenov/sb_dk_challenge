import os
import json
import asyncpg
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

mapping_table = sa.Table(
                'author_book_rel', metadata,
                sa.Column('author_id', sa.Integer, sa.ForeignKey(authors_table.c.id)),
                sa.Column('book_id', sa.Integer, sa.ForeignKey(books_table.c.id)),
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
        async with app.pool.acquire() as conn:
            result = await conn.fetchrow(self.table.insert().values(name=request.json['name'])) 
            try:
                return jsonify({'id': result['id']}, status=201)
            except Exception as e:
                return jsonify({'error': str(e)})

    @cors
    async def read(self, request, db_id=False):
        async with app.pool.acquire() as conn:
            if not db_id:
                result = [dict(r) for r in await conn.fetch(self.table.select())]
            else:
                try:
                    result = dict(await conn.fetchrow(self.table.select(self.table.c.id == db_id)))
                except TypeError:
                    return jsonify({'error': 'No matching record was found.'}, status=404)
            return jsonify({'result': result})
    
    @cors
    async def update(self, request, db_id):
        async with app.pool.acquire() as conn:
            try:
                modified = False
                columns = self.related.name.split('_')[:-1]
                related_name = [n for n in columns if n != self.table.name].pop()
                related_id = request.json.pop(related_name + '_id', None)
                if related_id:
                    rel_cols = [c + '_id' for c in columns]
                    values = {self.table.name + '_id': db_id,
                              related_name + '_id': related_id}
                    # Update related row in a single call preserving idempotency
                    # using from_select()
                    select = sa.select([values[rel_cols[0]], values[rel_cols[1]]]).where(
                        ~sa.exists(self.related.c).where(
                            sa.and_(self.related.c[rel_cols[0]] == values[rel_cols[0]],
                            self.related.c[rel_cols[1]] == values[rel_cols[1]])
                        )
                    )
                    insert = await conn.fetchval(
                        self.related.insert()
                            .from_select(rel_cols, select)
                            .returning(self.related.c[related_name + '_id'])
                    )
                    modified = bool(insert)
                if request.json:
                    row = await conn.fetchval(
                        self.table.update().values(**request.json)
                            .where(self.table.c.id == db_id)
                            .returning(self.table.c.id)
                    )
                    if not row:
                        return jsonify({'error': 'Not found.'}, status=404)
                    modified = True
                return jsonify(
                    {'result': 'Success' if modified else 'Relation already exists.'},
                    status=200 if modified else 304
                )
            except asyncpg.exceptions.ForeignKeyViolationError:
                return jsonify({'error': 'Invalid ID supplied.'}, status=400)

    
    @cors
    async def delete(self, request, db_id):
        async with app.pool.acquire() as conn:
            result = await conn.fetchval(
                self.table.delete().where(self.table.c.id == db_id).returning(self.table.c.id)
           )
            return jsonify(
                {'result': 'Success' if result else 'No matching record found.'},
                status=200 if result else 404
            )


    @cors
    async def count_related(self, request, db_id):
        async with app.pool.acquire() as conn:
            related_name = self.table.name + '_id'
            result = await conn.fetchval(
                sa.select([sa.func.count()])
                    .select_from(self.related)
                    .where(self.related.c[related_name] == db_id)
            )
            return jsonify({'result': result})


    @cors
    async def list_related(self, request, db_id):
        async with app.pool.acquire() as conn:
            field_names = self.related.name.split('_')[:-1]
            field_names.remove(self.table.name)
            related_name = field_names.pop()
            tables = {
                'author': authors_table,
                'book': books_table,
                'mapping': mapping_table
            }
            related_table = tables[related_name]
            mapping = tables['mapping']

            result = await conn.fetch(
                sa.select([related_table.c.id, related_table.c.name]).select_from(related_table
                    .join(mapping, related_table.c.id == mapping.c[related_name + '_id'])
                    .join(self.table, self.table.c.id == mapping.c[self.table.name + '_id'])
                )    
               .where(mapping.c[self.table.name + '_id'] == db_id)
            )
            return jsonify({'result': [dict(r) for r in result]})
                

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

            # Postgres docs suggest using COPY method for large bulk inserts,
            # here it comes for demonstrative purposes only.
            # ID column turned out not to auto increment on COPY that is why
            # populating name column explicitly.
            await conn.execute("COPY author(name) FROM '/initial_data/author'")
            await conn.execute("COPY book(name) FROM '/initial_data/book'")
            await conn.execute("COPY author_book_rel FROM '/initial_data/author_book_rel'")

