from os import getenv
from string import ascii_uppercase, ascii_lowercase, digits


class User:
    def __init__(self, id, firstname, lastname, username, password):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password


class UsersDB:
    def __init__(self, users):
        self.users = users

    def insert(self, user):
        if user.username in [u.username for u in self.users]:
            raise Exception(
                f"User with username '{user.username}' exists already!"
            )

        min_pw_len = int(getenv("MIN_PASSWORD_LEN"))
        max_pw_len = int(getenv("MAX_PASSWORD_LEN"))

        if not min_pw_len <= len(user.password) <= max_pw_len:
            raise Exception(
                "Password size must be between "
                f"{min_pw_len} and {max_pw_len}"
            )

        if all(d not in user.password for d in digits):
            raise Exception("Password must contain a number")

        if all(x not in user.password for x in ascii_uppercase):
            raise Exception("Password must contain an uppercase letter")

        if all(x not in user.password for x in ascii_lowercase):
            raise Exception("Password must contain a lowercase letter")

        self.users.append(user)

    def __teardown__(self):
        self.users = []
