import flask
from src.postgres_utils import setup_pg_db, read_from_pg_db, write_to_pg_db
import requests
import pymongo
import pika
from src.redis_utils import read_key_from_redis, write_key_to_redis
from flask import jsonify

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

@app.route("/postgres/read")
def postgres_read_test():
    results  = read_from_pg_db()
    return jsonify(results)

@app.route("/postgres/write/<user_id>/<user_name>")
def postgres_write_test(user_id, user_name):
    write_to_pg_db(user_id,user_name)
    resp = jsonify(success=True)
    return resp

def main():
    setup_pg_db()
    app.run(host='localhost', port=8082)

if __name__ == '__main__':
    print('running flask server...')
    main()


