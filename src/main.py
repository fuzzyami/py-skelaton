from cluster_scanner import scan_cluster
import json
import deployments
from flask_apscheduler import APScheduler
import flask
from flask import request
from src.postgres_utils import setup_pg_db, read_from_pg_db, write_to_pg_db
import requests
import pymongo
from utils import parse_json
import sys

import pika
import k8s_api
from bson import json_util
from src.redis_utils import read_key_from_redis, write_key_to_redis
from flask import jsonify

# mongo connection
client = pymongo.MongoClient('localhost', 27017, username='root', password='example')

# create flask app
app = flask.Flask(__name__)


@app.route("/deployments")
def list_deployments():
    return jsonify(deployments.get_deployments())

# write a POST endpoint for policies
@app.route("/policies", methods=['POST'])
def post_policy():
    # takes a single policy and writes it to the database, overwriting if needed

    # sanity: is there such a namespace? a deployment?
    # sanity do we have all the fields that are expected?

    # a policy is unique by namespace and deployment
    policy = request.json

    # write to mongo
    db = client['autoscaler']
    collection = db['policies']
    collection.insert_one(parse_json(policy))
    return jsonify(policy)

def start_server():

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    scheduler.add_job(id='scan_cluster', func=scan_cluster, trigger='interval', seconds=1)
    


    app.run(host='localhost',debug=False, port=8082)


if __name__ == '__main__':
    start_server()