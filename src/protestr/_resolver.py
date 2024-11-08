from random import randint, uniform, choice as randchoice, choices as randchoices
from string import ascii_letters


def resolve(spec):
    if spec is int:
        return randint(0, 1000)

    if spec is float:
        return uniform(0, 1000)

    if spec is complex:
        return complex(real=uniform(-1000, 1000), imag=uniform(-1000, 1000))

    if spec is bool:
        return randchoice((True, False))

    if spec is str:
        return "".join(randchoices(ascii_letters, k=randint(1, 50)))

    if isinstance(spec, tuple):
        return tuple(resolve(x) for x in spec)

    if isinstance(spec, list):
        return [resolve(x) for x in spec]

    if isinstance(spec, set):
        return {resolve(x) for x in spec}

    if isinstance(spec, dict):
        return {resolve(k): resolve(v) for k, v in spec.items()}

    if callable(spec):
        return resolve(spec())

    return spec
