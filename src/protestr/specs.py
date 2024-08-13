def between(start, stop):
    return "protestr.specs.between", start, stop


def either(*options):
    return "protestr.specs.either", options


def subset(superset, n):
    return "protestr.specs.subset", superset, n


def sequence(each, n, type=None):
    return "protestr.specs.sequence", each, n, type
