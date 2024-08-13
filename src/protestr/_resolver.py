from random import randint, uniform, choice, choices, sample
from string import ascii_letters


def resolve(spec):
    if spec is int:
        return randint(0, 1000)

    if spec is float:
        return uniform(0, 1000)

    if spec is complex:
        return complex(
            real=uniform(-1000, 1000),
            imag=uniform(-1000, 1000)
        )

    if spec is bool:
        return choice((True, False))

    if spec is str:
        return "".join(choices(ascii_letters, k=randint(1, 50)))

    if isinstance(spec, dict):
        return {resolve(k): resolve(v) for k, v in spec.items()}

    match spec:
        case "protestr.specs.between", start, stop:
            start = resolve(start)
            stop = resolve(stop)
            if isinstance(start, int) and isinstance(stop, int):
                return randint(start, stop)
            return uniform(start, stop)

        case "protestr.specs.either", options:
            return choice(options)

        case "protestr.specs.subset", superset, n:
            return sample(superset, resolve(n))

        case "protestr.specs.sequence", spec, n, seq_type:
            gen = (resolve(spec) for _ in range(resolve(n)))
            return seq_type(gen) if seq_type else gen

    if callable(spec):
        return spec()

    return spec
