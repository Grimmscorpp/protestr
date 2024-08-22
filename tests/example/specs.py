from protestr import provide
from protestr.specs import between, choice, choices
from string import ascii_uppercase, ascii_lowercase, digits
from tests.example.fakes import User, UsersDB


@provide(
    digit=choice(digits),                # password to contain a
    uppercase=choice(ascii_uppercase),   # number, an uppercase and a
    lowercase=choice(ascii_lowercase),   # lowercase letter, and be
    chars=choices(str, k=between(5, 12)) # 8–15 characters long
)
def password(uppercase, lowercase, digit, chars):
    return "".join((uppercase, lowercase, digit, chars))


@provide(
    id=str,
    firstname=choice("John", "Jane", "Orange"),
    lastname=choice("Smith", "Doe", "Carrot"),
    username=choices(ascii_lowercase, k=between(5, 10)),
    password=password
)
def user(id, firstname, lastname, username, password):
    return User(id, firstname, lastname, username, password)


@provide(users=3*[user])
def testdb(users):
    return UsersDB(users)
