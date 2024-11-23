import os
import pymongo
import redis
import json


def add_to_users_db(users):
    if not users:
        return

    client = pymongo.MongoClient(
        host=os.environ["MONGO_DB_HOST"],
        port=27017,
    )

    client.users_db.users.insert_many([{"id": u.id, "name": u.name} for u in users])

    client.close()


_cache = redis.Redis(
    host="localhost",
    port=6379,
    password="",
    decode_responses=True,
)


def cached(fn):
    def cached(*args, **kwds):
        key = f"{fn.__module__}.{fn.__name__}"

        if _cache.exists(key) == 0:
            _cache.set(key, json.dumps(fn(*args, **kwds)))

        return json.loads(_cache.get(key))

    return cached
