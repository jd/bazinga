import cPickle
from decorator import decorator

def _memoize(func, *args, **kwargs):
    if func._ignore_first and len(args) > 0:
        key = cPickle.dumps((args[1:], kwargs))
    else:
        key = cPickle.dumps((args, kwargs))

    try:
        return func._cache[key]
    except KeyError:
        func._cache[key] = func(*args, **kwargs)
        return func._cache[key]

def memoize(cache={}, ignore_first=True):
    """Decorator to memoize a function."""
    def memoize_decorator(func):
        func._cache = cache
        func._ignore_first = ignore_first
        return decorator(_memoize, func)
    return memoize_decorator
