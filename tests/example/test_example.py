import unittest
from unittest.mock import patch, call
from protestr import provide, resolve
from protestr.specs import choice, choices
from string import (
    ascii_lowercase, ascii_uppercase, ascii_letters, digits
)
import tests.example.specs as specs


class TestExample(unittest.TestCase):
    @provide(
        db=specs.testdb,
        user=specs.user
    )
    def test_insert_user_with_existing_username_fails(self, db, user):
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
        db=specs.testdb,
        user=specs.user,
        shortpass=choices(str, k=7),
        longpass=choices(str, k=16)
    )
    @patch("tests.example.fakes.getenv")
    def test_insert_user_with_invalid_password_lengths_fails(
        self, getenv, db, user, shortpass, longpass
    ):
        getenv.side_effect = lambda env: \
            8 if env == "MIN_PASSWORD_LEN" else 15

        for pw in (shortpass, longpass):
            user.password = pw

            try:
                db.insert(user)
            except Exception as e:
                message, = e.args

            self.assertEqual(
                message, "Password size must be between 8 and 15"
            )

        self.assertEqual(getenv.mock_calls, [
            call("MIN_PASSWORD_LEN"),
            call("MAX_PASSWORD_LEN"),
            call("MIN_PASSWORD_LEN"),
            call("MAX_PASSWORD_LEN")
        ])

    @provide(
        db=specs.testdb,
        user=specs.user,
        letters_only=choices(ascii_letters, k=8)
    )
    @patch("tests.example.fakes.getenv")
    def test_insert_user_with_no_digits_in_password_fails(
        self, getenv, db, user, letters_only
    ):
        getenv.side_effect = lambda env: \
            8 if env == "MIN_PASSWORD_LEN" else 15

        user.password = letters_only

        try:
            db.insert(user)
        except Exception as e:
            message, = e.args

        self.assertEqual(
            message, "Password must contain a number"
        )

        self.assertEqual(getenv.mock_calls, [
            call("MIN_PASSWORD_LEN"),
            call("MAX_PASSWORD_LEN")
        ])

    @provide(
        db=specs.testdb,
        user=specs.user,
        digits=choices(digits, k=5),
        lowercase=choices(ascii_lowercase, k=5)
    )
    @patch("tests.example.fakes.getenv")
    def test_insert_user_with_no_uppercase_in_password_fails(
        self, getenv, db, user, digits, lowercase
    ):
        getenv.side_effect = lambda env: \
            8 if env == "MIN_PASSWORD_LEN" else 15

        user.password = digits + lowercase

        try:
            db.insert(user)
        except Exception as e:
            message, = e.args

        self.assertEqual(
            message, "Password must contain an uppercase letter"
        )

        self.assertEqual(getenv.mock_calls, [
            call("MIN_PASSWORD_LEN"),
            call("MAX_PASSWORD_LEN")
        ])

    @provide(
        db=specs.testdb,
        user=specs.user,
        digits=choices(digits, k=5),
        uppercase=choices(ascii_uppercase, k=5)
    )
    @patch("tests.example.fakes.getenv")
    def test_insert_user_with_no_lowercase_in_password_fails(
        self, getenv, db, user, digits, uppercase
    ):
        getenv.side_effect = lambda env: \
            8 if env == "MIN_PASSWORD_LEN" else 15

        user.password = digits + uppercase

        try:
            db.insert(user)
        except Exception as e:
            message, = e.args

        self.assertEqual(
            message, "Password must contain a lowercase letter"
        )

        self.assertEqual(getenv.mock_calls, [
            call("MIN_PASSWORD_LEN"),
            call("MAX_PASSWORD_LEN")
        ])

    @provide(
        db=specs.testdb,
        user=specs.user
    )
    @patch("tests.example.fakes.getenv")
    def test_insert_user_with_unique_username_and_valid_password_passes(
        self, getenv, db, user
    ):
        getenv.side_effect = lambda env: \
            8 if env == "MIN_PASSWORD_LEN" else 15

        db.insert(user)

        self.assertIn(user, db.users)

        self.assertEqual(getenv.mock_calls, [
            call("MIN_PASSWORD_LEN"),
            call("MAX_PASSWORD_LEN")
        ])


if __name__ == "__main__":
    unittest.main()
