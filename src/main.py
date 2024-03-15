import flask
import psycopg2
import requests
import pymongo
import pika
import redis

# create flask app
app = flask.Flask(__name__)

@app.route("/hello-world")
def hello_world():
    return "<p>Hello, World!</p>"

def main():
    app.run(host='localhost', port=8082)

if __name__ == '__main__':
    print('running flask server...')
    main()


