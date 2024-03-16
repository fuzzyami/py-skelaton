import flask
from src.postgres_utils import setup_pg_db, read_from_pg_db, write_to_pg_db
import requests
import pymongo
import sys
import pika
from src.redis_utils import read_key_from_redis, write_key_to_redis
from flask import jsonify

# mongo connection
client = pymongo.MongoClient('localhost', 27017, username='root', password='example')

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
    results = read_from_pg_db()
    return jsonify(results)


@app.route("/postgres/write/<user_id>/<user_name>")
def postgres_write_test(user_id, user_name):
    write_to_pg_db(user_id, user_name)
    resp = jsonify(success=True)
    return resp


# mongo test endpoint
@app.route("/mongo/write/<name>")
def mongo_write_test(name):
    db = client['mydb']
    collection = db['mycollection']
    collection.insert_one({'name': name})
    return f'Wrote {name} to mongo'


# mongo read endpoint
@app.route("/mongo/read")
def mongo_read_test():
    db = client['mydb']
    collection = db['mycollection']
    results = collection.find({})
    results = [result['name'] for result in results]
    return jsonify(results)

# pika test endpoint
@app.route("/pika/write/<message>")
def pika_write_test(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='myqueue')
    channel.basic_publish(exchange='', routing_key='myqueue', body=message)
    connection.close()
    return f'Wrote {message} to pika'


def start_server():
    setup_pg_db()
    app.run(host='localhost', port=8082)

def start_worker():
    # read message from pika
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='myqueue')
    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
    channel.basic_consume(queue='myqueue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'worker':
        start_worker()
    else:
        start_server()