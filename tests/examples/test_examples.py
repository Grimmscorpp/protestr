import unittest
from unittest.mock import patch
from protestr import provide, resolve
from protestr.specs import between, choice, choices, recipe
from string import (
    ascii_lowercase, ascii_uppercase, ascii_letters, digits
)
import tests.examples.specs as specs


def factorial(n):
    if n < 0:
        raise Exception("n must be non-negative")

    if int(n) != n:
        raise Exception("n must be an integer")

    return 1 if n < 2 else n * factorial(n - 1)


class TestExamples(unittest.TestCase):
    @provide(n=9, expected=362880)
    @provide(n=5, expected=120)
    @provide(n=1, expected=1)
    @provide(n=0, expected=1)
    def test_factorial_valid_number(self, n, expected):
        self.assertEqual(factorial(n), expected)

    @provide(n=1.5, expected="n must be an integer")
    @provide(n=between(-10000, -1), expected="n must be non-negative")
    def test_factorial_invalid_number(self, n, expected):
        try:
            factorial(n)
        except Exception as e:
            message, = e.args

        self.assertEqual(message, expected)

    @provide(
        db=specs.testdb,
        user=specs.user
    )
    def test_insert_user_with_existing_username(self, db, user):
        user.username = resolve(choice(db.users)).username

        try:
            db.insert(user)
        except Exception as e:
            message, = e.args

        self.assertEqual(
            message,
            f"User with username '{user.username}' exists already!"
        )

    @provide(
        password=recipe(
            choices(digits, k=5),
            choices(ascii_uppercase, k=5),
            then="".join
        ),
        expected="Password must contain a lowercase letter",
        db=specs.testdb,
        user=specs.user
    )
    @provide(
        password=recipe(
            choices(digits, k=5),
            choices(ascii_lowercase, k=5),
            then="".join
        ),
        expected="Password must contain an uppercase letter",
        db=specs.testdb,
        user=specs.user
    )
    @provide(
        password=choices(ascii_letters, k=8),
        expected="Password must contain a number",
        db=specs.testdb,
        user=specs.user
    )
    @provide(
        password=choices(str, k=7),
        expected="Password must be at least 8 chars",
        db=specs.testdb,
        user=specs.user
    )
    @patch("tests.examples.fakes.os.getenv")
    def test_insert_user_with_invalid_password(
        self, getenv, db, user, password, expected
    ):
        getenv.side_effect = [8]

        user.password = password

        try:
            db.insert(user)
        except Exception as e:
            message, = e.args

        self.assertEqual(message, expected)

        getenv.assert_called_once_with("MIN_PASSWORD_LEN")

    @provide(
        db=specs.testdb,
        user=specs.user
    )
    @patch("tests.examples.fakes.os.getenv")
    def test_insert_user_with_unique_username_and_valid_password(
        self, getenv, db, user
    ):
        getenv.side_effect = [8]

        db.insert(user)

        self.assertIn(user, db.users)

        getenv.assert_called_once_with("MIN_PASSWORD_LEN")


if __name__ == "__main__":
    unittest.main()
