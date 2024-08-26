def provide(**specs):
    def provider(func):
        if hasattr(func, "__specslist__"):
            func.__specslist__.append(specs)
            return func

        def provided(*args, **kwds):
            from protestr import resolve

            for specs in provided.__specslist__:
                try:
                    resolved = {
                        k: resolve(s) for k, s in (specs|kwds).items()
                    }
                    result = func(*args, **resolved)
                finally:
                    _teardown(resolved.values())

            return result

        provided.__specslist__ = [specs]
        return provided

    return provider


def _teardown(values):
    for v in values:
        is_collection = isinstance(v, tuple) or \
            isinstance(v, list) or \
            isinstance(v, set)

        if is_collection:
            _teardown(v)

        if hasattr(v, "__teardown__"):
            v.__teardown__()
