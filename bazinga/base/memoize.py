import cPickle
from threading import Lock
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


class MemoizedMeta(type):
    """Singleton metaclass."""

    __lock = Lock()

    @memoize()
    def __call__(cls, *args, **kwargs):
        with MemoizedMeta.__lock:
            return super(MemoizedMeta, cls).__call__(*args, **kwargs)


class Memoized(object):
    """Pool of memoized object. Like a big bag of singletons."""

    __metaclass__ = MemoizedMeta
