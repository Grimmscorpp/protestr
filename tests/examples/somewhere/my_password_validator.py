from string import digits, ascii_uppercase, ascii_lowercase


def validate(password):
    if len(password) < 8:
        raise Exception("Password should be at least 8 chars")

    if all(c not in digits for c in password):
        raise Exception("Password should contain a number")

    if all(c not in ascii_uppercase for c in password):
        raise Exception("Password should contain an uppercase letter")

    if all(c not in ascii_lowercase for c in password):
        raise Exception("Password should contain a lowercase letter")
