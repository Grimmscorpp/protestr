def provide(**specs):
    def decorator(orig_func):
        def provide_resolved_specs(*orig_args, **orig_kwds):
            from protestr import resolve

            try:
                resolved_specs = {
                    k: resolve(s) for k, s in (specs|orig_kwds).items()
                }
                result = orig_func(*orig_args, **resolved_specs)
            finally:
                failures = []

                _teardown(resolved_specs.values(), failures)

                if failures:
                    raise(Exception(*failures))

            return result

        return provide_resolved_specs

    return decorator


def _teardown(values, failures):
    for v in values:
        try:
            is_collection = isinstance(v, tuple) or \
                isinstance(v, list) or \
                isinstance(v, set)

            if is_collection:
                _teardown(v, failures)

            if hasattr(v, "__teardown__"):
                v.__teardown__()
        except Exception as e:
            failures.append(e)
