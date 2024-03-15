import flask
import psycopg2
import requests
import pymongo
import pika
from src.redis_utils import read_key_from_redis, write_key_to_redis

# create flask app
app = flask.Flask(__name__)

@app.route("/hello-world")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/redis/write/<key>/<value>")
def redis_write_test(key, value):
    write_key_to_redis(key, value)
    return f'Wrote {value} to {key}'

@app.route("/redis/read/<key>")
def redis_read_test(key):
    return read_key_from_redis(key)


def main():
    app.run(host='localhost', port=8082)

if __name__ == '__main__':
    print('running flask server...')
    main()


