import redis


def get_redis_connection():
    return redis.StrictRedis(host='localhost', port=6379, db=0)

def read_key_from_redis(key):
    conn = get_redis_connection()
    return conn.get(key)

def write_key_to_redis(key, value):
    conn = get_redis_connection()
    conn.set(key, value)
