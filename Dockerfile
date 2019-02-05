FROM python:3.5-slim
MAINTAINER Dmitry Lashchenov


# Start Installing the Basic Dependencies
RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install gunicorn

RUN mkdir -p /sanic/config
RUN mkdir -p /sanic/bookstore

COPY config/* /sanic/config/
COPY bookstore/ /sanic/bookstore/
COPY tests/ /sanic/tests/
COPY requirements.txt /sanic
COPY run.py /sanic/run.py
COPY .env /sanic/.env

WORKDIR /sanic
RUN pip install -r requirements.txt
RUN find . -type f

ENV SANIC_SERVER_PORT 8000
ENV SANIC_SERVER_HOST 0.0.0.0

EXPOSE 8000


ENTRYPOINT ["gunicorn", "run:app", "--config", "/sanic/config/gunicorn.conf", "--log-config", "/sanic/config/logging.conf", "-b", "0.0.0.0:8000", "--worker-class",  "sanic.worker.GunicornWorker"]

