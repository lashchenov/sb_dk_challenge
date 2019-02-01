import os
import json
import asyncio
import datetime

import uvloop

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from aiopg.sa import create_engine

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

class Author(Base):
    __tablename__ = 'author'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(32))
    books = sa.orm.relationship('Book', secondary=mapping_table, back_populates='authors')


class Book(Base):
    __tablename__ = 'book'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(128))
    authors = sa.orm.relationship('Author', secondary=mapping_table, back_populates='books')


app = Sanic(__name__)




app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)

app.blueprint(health)




@app.route("/")
async def default(request):
    async with create_engine(connection) as engine:
        async with engine.acquire() as conn:
            books = []
            async for book in conn.execute(books_table.select()):
                books.append(book.name)
            authors = []
            async for author in conn.execute(authors_table.select()):
                authors.append(author.name)
            return jsonify({'result': {'authors': authors, 'books': books}})    


@app.listener('before_server_start')
async def prepare_db(app, loop):
    async with create_engine(connection) as engine:
        async with engine.acquire() as conn:
            await conn.execute('DROP TABLE IF EXISTS author')
            await conn.execute('DROP TABLE IF EXISTS book')
            await conn.execute('DROP TABLE IF EXISTS author_book_rel')
            await conn.execute("""CREATE TABLE author (
                                   id serial primary key,
                                   name varchar(32)
                               );
                               CREATE TABLE book (
                                   id serial primary key,
                                   name varchar(128)
                               );
                               CREATE TABLE author_book_rel (
                                   author_id integer not null,
                                   book_id integer not null
                               );""")
            with open('bookstore/initial.json', 'r') as fixture:
                data = json.loads(fixture.read())
                authors, books, mapping = (data[k] for k in ['authors', 'books', 'map'])
                for author in authors:
                    await conn.execute(authors_table.insert().values(name=author))
                for book in books:
                    await conn.execute(books_table.insert().values(name=book))
                for i, link in enumerate(mapping):
                    for book in link:
                        await conn.execute(mapping_table.insert().values(author_id=i+1, book_id=book))

