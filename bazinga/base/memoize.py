import cPickle
from decorator import decorator

def _memoize(func, *args, **kwargs):
    key = cPickle.dumps((args, kwargs))

    try:
        return func.cache[key]
    except KeyError:
        func.cache[key] = func(*args, **kwargs)
        return func.cache[key]

def memoize(cache={}):
    """Decorator to memoize a function."""
    def memoize_decorator(func):
        func.cache = cache
        return decorator(_memoize, func)
    return memoize_decorator
