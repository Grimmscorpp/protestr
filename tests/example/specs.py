from protestr import provide
from protestr.specs import between, single, merged, permutation
from string import (
    ascii_letters, ascii_uppercase, ascii_lowercase, digits
)
from tests.example.fakes import User, UsersDB


@provide(
    id=str,
    firstname=single("John", "Jane", "Orange"),
    lastname=single("Smith", "Doe", "Carrot"),
    username=permutation(ascii_letters, k=between(5, 10)),
    password=merged(
        single(digits),                     # password to contain a
        single(ascii_uppercase),            # number, an uppercase and
        single(ascii_lowercase),            # a lowercase letter and be
        permutation(str, k=between(5, 12)), # 8–15 characters long
        func="".join
    )
)
def user(id, firstname, lastname, username, password):
    return User(id, firstname, lastname, username, password)


@provide(users=3*[user])
def testdb(users):
    return UsersDB(users)
