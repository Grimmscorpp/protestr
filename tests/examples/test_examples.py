import unittest
from unittest.mock import patch
from protestr import provide, resolve
from protestr.specs import choice, choices, recipe
from string import (
    ascii_lowercase, ascii_uppercase, ascii_letters, digits
)
import tests.examples.specs as specs
from tests.examples.somewhere import my_password_validator as validator


class TestExamples(unittest.TestCase):
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


class TestPasswordValidator(unittest.TestCase):
    @provide(
        password=recipe(
            choices(ascii_uppercase, k=4),
            choices(ascii_lowercase, k=4),
            choices(digits, k=4),
            then="".join
        ),
        expected=None
    )
    @provide(
        password=recipe(
            choices(ascii_uppercase, k=4),
            choices(digits, k=4),
            then="".join
        ),
        expected="Password should contain a lowercase letter"
    )
    @provide(
        password=recipe(
            choices(ascii_lowercase, k=4),
            choices(digits, k=4),
            then="".join
        ),
        expected="Password should contain an uppercase letter"
    )
    @provide(
        password=choices(ascii_letters, k=8),
        expected="Password should contain a number"
    )
    @provide(
        password=choices(str, k=7),
        expected="Password should be at least 8 chars"
    )
    def test_validate(self, password, expected):
        try:
            validator.validate(password)
        except Exception as ex:
            message, = ex.args
            self.assertEqual(message, expected)
        else:
            self.assertIsNone(expected)

    def test_validate_short_password(self):
        try:
            validator.validate("short")
        except Exception as ex:
            message, = ex.args

        self.assertEqual(message, "Password should be at least 8 chars")

    def test_validate_letters_only(self):
        try:
            validator.validate("letters only")
        except Exception as ex:
            message, = ex.args

        self.assertEqual(message, "Password should contain a number")

    def test_validate_lowercase_and_digits(self):
        try:
            validator.validate("lowercase and 1 digit")
        except Exception as ex:
            message, = ex.args

        self.assertEqual(
            message, "Password should contain an uppercase letter"
        )

    def test_validate_uppercase_and_digits(self):
        try:
            validator.validate("UPPERCASE AND 1 DIGIT")
        except Exception as ex:
            message, = ex.args

        self.assertEqual(
            message, "Password should contain a lowercase letter"
        )

    def test_validate_both_cases_and_digits(self):
        try:
            validator.validate("UPPERCASE, lowercase, and 1 digit")
        except Exception:
            raise


if __name__ == "__main__":
    unittest.main()
