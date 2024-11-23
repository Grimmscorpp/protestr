from protestr import provide
from protestr.specs import between
import docker
import pymongo
import time


@provide(id=between(1, 99), name=str, password=str)
class User:
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password


class MongoDB:
    def __init__(self):
        self.container = docker.from_env().containers.run(
            "mongo", detach=True, ports={27017: 27017}
        )
        self.client = pymongo.MongoClient("localhost", 27017)

    def __teardown__(self):
        self.client.close()
        self.container.stop()
        self.container.remove()


class Redis:
    def __init__(self):
        self.container = docker.from_env().containers.run(
            "redis:8.0-M02", detach=True, ports={6379: 6379}
        )

        # wait for the port
        time.sleep(0.1)

    def __teardown__(self):
        self.container.stop()
        self.container.remove()


@provide(
    latitude=between(-90.0, 90.0),
    longitude=between(-180.0, 180.0),
    altitude=float,
)
def geo_coordinate(latitude, longitude, altitude):
    return latitude, longitude, altitude
