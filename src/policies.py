import pymongo

# mongo connection
client = pymongo.MongoClient('localhost', 27017, username='root', password='example')

def get_policy(namespace, deployment_name):
    # get the policy from the database
    db = client['autoscaler']
    collection = db['policies']
    # mongo has an index on namespace and deployment: it's unique
    return collection.find_one({"deployment.namespace": namespace, "deployment.name": deployment_name})

