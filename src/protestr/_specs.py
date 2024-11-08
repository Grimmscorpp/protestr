from random import (
    randint,
    uniform,
    sample as randsample,
    choice as randchoice,
    choices as randchoices,
)
from protestr import resolve


def between(x, y):
    def spec():
        m, n = sorted((resolve(x), resolve(y)))

        if isinstance(m, int) and isinstance(n, int):
            return randint(m, n)

        return uniform(m, n)

    return spec


def choice(*elems):
    return lambda: randchoice(resolve(_unpack_if_single(elems)))


def sample(*elems, k):
    def spec():
        resolved_elems = resolve(_unpack_if_single(elems))

        return _cast(
            result=randsample(
                population=resolved_elems,
                k=resolve(k) if k else len(resolved_elems),
            ),
            elemtype=type(resolved_elems),
        )

    return spec


def choices(*elems, k):
    def spec():
        resolved_elems = resolve(_unpack_if_single(elems))

        return _cast(
            result=randchoices(
                population=resolved_elems,
                k=resolve(k) if k else len(resolved_elems),
            ),
            elemtype=type(resolved_elems),
        )

    return spec


def recipe(*specs, then):
    return lambda: then(resolve(_unpack_if_single(specs)))


def _cast(result, elemtype):
    return (
        "".join(result)
        if elemtype is str
        else (*result,)
        if elemtype is tuple
        else result
    )


def _unpack_if_single(elems):
    them = (*elems,)
    return them[0] if len(them) == 1 else them
