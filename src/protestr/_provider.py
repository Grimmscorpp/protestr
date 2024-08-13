def provide(*specs, **kwdspecs):
    def decorator(orig_func):
        def provide_resolved_specs(*orig_args, **orig_kwds):
            from protestr import resolve

            return orig_func(
                *(resolve(s) for s in specs),
                **{k: resolve(s) for k, s in kwdspecs.items()}
            )

        return provide_resolved_specs

    return decorator
