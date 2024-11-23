def provide(**specs):
    def provider(func):
        if hasattr(func, "__specslist__"):
            func.__specslist__.append(specs)
            return func

        def provided(*args, **kwds):
            from protestr import resolve

            all_specs = {}

            for specs in reversed(provided.__specslist__):
                all_specs |= specs | kwds

                resolved = {}

                try:
                    for k, s in all_specs.items():
                        resolved[k] = resolve(s)

                    result = func(*args, **resolved)
                finally:
                    _teardown(resolved.values())

            return result

        provided.__specslist__ = [specs]
        return provided

    return provider


def _teardown(values):
    for v in values:
        is_collection = (
            isinstance(v, tuple) or isinstance(v, list) or isinstance(v, set)
        )

        if is_collection:
            _teardown(v)

        if hasattr(v, "__teardown__"):
            v.__teardown__()
