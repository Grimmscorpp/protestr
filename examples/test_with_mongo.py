import unittest
from unittest.mock import patch as mock
from protestr import provide
from examples.specs import User, MongoDB
from examples.lib import add_to_users_db


class TestWithMongo(unittest.TestCase):
    @provide(
        users=[User] * 3,
        mongo=MongoDB,
    )
    @provide(users=[])
    @mock("examples.lib.os")
    def test_add_to_users_db_should_add_all_users(self, os, users, mongo):
        os.environ.__getitem__.return_value = "localhost"

        add_to_users_db(users)

        added = mongo.client.users_db.users.count_documents({})
        self.assertEqual(added, len(users))


if __name__ == "__main__":
    unittest.main()
