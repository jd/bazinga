import cPickle
from threading import Lock
from decorator import decorator

def _memoize(func, *args, **kwargs):
    with func._memoize_lock:
        if func._memoize_ignore_first and len(args) > 0:
            key = cPickle.dumps((args[1:], kwargs))
        else:
            key = cPickle.dumps((args, kwargs))

        try:
            return func._memoize_cache[key]
        except KeyError:
            # Cache can be weak, so store it explicitly in a var
            value = func(*args, **kwargs)
            func._memoize_cache[key] = value
            return value

def memoize(cache={}, ignore_first=True):
    """Decorator to memoize a function."""
    def memoize_decorator(func):
        func._memoize_cache = cache
        func._memoize_lock = Lock()
        func._memoize_ignore_first = ignore_first
        return decorator(_memoize, func)
    return memoize_decorator


class MemoizedMeta(type):
    """Singleton metaclass."""

    @memoize()
    def __call__(cls, *args, **kwargs):
        return super(MemoizedMeta, cls).__call__(*args, **kwargs)


class Memoized(object):
    """Pool of memoized object. Like a big bag of singletons."""

    __metaclass__ = MemoizedMeta
