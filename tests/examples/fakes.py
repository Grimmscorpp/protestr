import os
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

        min_pw_len = int(os.getenv("MIN_PASSWORD_LEN"))

        if len(user.password) < min_pw_len:
            raise Exception(
                f"Password must be at least {min_pw_len} chars"
            )

        if all(c not in digits for c in user.password):
            raise Exception("Password must contain a number")

        if all(c not in ascii_uppercase for c in user.password):
            raise Exception("Password must contain an uppercase letter")

        if all(c not in ascii_lowercase for c in user.password):
            raise Exception("Password must contain a lowercase letter")

        self.users.append(user)

    def __teardown__(self):
        self.users = []
