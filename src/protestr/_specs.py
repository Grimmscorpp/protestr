from random import randint, uniform, sample, choice, choices
from protestr import resolve


def between(x, y):
    def spec():
        m, n = sorted((resolve(x), resolve(y)))

        if isinstance(m, int) and isinstance(n, int):
            return randint(m, n)

        return uniform(m, n)

    return spec


def single(*elems):
    return lambda: choice(resolve(_unpack(elems)))


def combination(*elems, k):
    def spec():
        resolved_elems = resolve(_unpack(elems))

        return _cast(
            result=sample(
                population=resolved_elems,
                k=resolve(k) if k else len(resolved_elems)
            ),
            elemtype=type(resolved_elems)
        )

    return spec


def permutation(*elems, k):
    def spec():
        resolved_elems = resolve(_unpack(elems))

        return _cast(
            result=choices(
                population=resolved_elems,
                k=resolve(k) if k else len(resolved_elems)
            ),
            elemtype=type(resolved_elems)
        )

    return spec


def merged(*specs, func):
    return lambda: func(resolve(_unpack(specs)))


def _cast(result, elemtype):
    return "".join(result) if elemtype is str else \
        (*result,) if elemtype is tuple else result

def _unpack(elems):
    them = tuple(elems)
    return them if len(them) > 1 else them[0]
