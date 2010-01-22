import cPickle
from decorator import decorator

def _memoize(func, *args, **kwargs):
    key = cPickle.dumps((args, kwargs))

    try:
        return func.cache[key]
    except KeyError:
        func.cache[key] = func(*args, **kwargs)
        return func.cache[key]

def memoize(func):

    """Decorator to memoize a function."""

    func.cache = {}
    return decorator(_memoize, func)
