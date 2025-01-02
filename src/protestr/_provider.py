from inspect import signature


def provide(*specs, **kwspecs):
    def provider(fn):
        if hasattr(fn, "__fixture_patches__"):
            fn.__fixture_patches__.append(_combine(specs, kwspecs))
            return fn

        def provided(*args, **kwds):
            from protestr import resolve

            first = provided.__fixture_patches__[-1]
            overridden_specs = {}
            other_kwds = {}

            for k, v in kwds.items():
                if k in first:
                    overridden_specs[k] = v
                else:
                    other_kwds[k] = v

            for patch in reversed(provided.__fixture_patches__):
                fixture = first | patch | overridden_specs

                resolved = {}

                try:
                    for k, s in fixture.items():
                        resolved[k] = resolve(s)

                    requested_kwds = {
                        k: v
                        for k, v in resolved.items()
                        if k in signature(fn).parameters
                    }

                    result = fn(*args, **(requested_kwds | other_kwds))
                finally:
                    _teardown(resolved.values())

            return result

        provided.__fixture_patches__ = [_combine(specs, kwspecs)]
        return provided

    return provider


def _combine(specs, kwspecs):
    return {f"spec[{i}]": spec for i, spec in enumerate(specs)} | kwspecs


def _teardown(values):
    for v in values:
        if isinstance(v, tuple) or isinstance(v, list) or isinstance(v, set):
            _teardown(v)
        elif isinstance(v, dict):
            _teardown(v.values())

        if hasattr(v, "__teardown__"):
            v.__teardown__()
