import os
import pymongo


def add_to_users_db(users):
    if not users:
        return

    client = pymongo.MongoClient(
        host=os.environ["MONGO_DB_HOST"],
        port=27017,
    )

    client.users_db.users.insert_many([{"id": u.id, "name": u.name} for u in users])

    client.close()
