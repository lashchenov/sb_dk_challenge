import os
import asyncio
import datetime

import uvloop

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from aiopg.sa import create_engine

from sanic import Sanic
from sanic.response import json
from sanic_openapi import swagger_blueprint, openapi_blueprint, doc
from bookstore.blueprint.health import health

# db_user = 'postgres'
db_user = db_host = os.environ['SANIC_DB_HOST']
db_name = os.environ['SANIC_DB_DATABASE']
db_password = os.environ['SANIC_DB_PASSWORD']

connection = 'postgres://{u}:{up}@{h}/{hp}'.format(u=db_user, up=db_password, h=db_host, hp=db_name)

metadata = sa.MetaData()
Base = declarative_base()

link_table = sa.Table(
                'author_book_rel', metadata,
                sa.Column('author_id', sa.Integer, sa.ForeignKey('author.id')),
                sa.Column('book_id', sa.Integer, sa.ForeignKey('book.id')),
             )


class Author(Base):
    __tablename__ = 'author'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(32))
    books = sa.orm.relationship('Book', secondary=link_table, back_populates='authors')


class Book(Base):
    __tablename__ = 'book'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(64))
    authors = sa.orm.relationship('Author', secondary=link_table, back_populates='books')


app = Sanic(__name__)




app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)

app.blueprint(health)




@app.route("/")
async def default(request):
    return json({"message": "hello Sanic!"})


@app.listener('before_server_start')
async def prepare_db(app, loop):
    async with create_engine(connection) as engine:
        async with engine.acquire() as conn:
            await conn.execute("""CREATE TABLE author (
                id serial primary key,
                name varchar(32)
            );""")

