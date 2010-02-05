from threading import Lock
import weakref
import cPickle

class SingletonMeta(type):
    """Singleton metaclass."""

    def __call__(cls, *args, **kwargs):
        obj, do_init = cls.__new__(cls, *args, **kwargs)
        if obj is not None and do_init:
            cls.__init__(obj, *args, **kwargs)
        return obj


class Singleton(object):
    """Singleton class."""

    __metaclass__ = SingletonMeta

    # The singleton instance.
    __instance = None
    __instance_lock = Lock()

    def __new__(cls, *args, **kwargs):
        """Create a singleton. Return always the same instance of a class."""
        with cls.__instance_lock:
            if cls.__instance is None:
                cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
                return cls.__instance, True
        return cls.__instance, False


class SingletonPoolMeta(type):
    """Singleton pool metaclass."""

    def __call__(cls, *args, **kwargs):
        try:
            with cls.__instance_lock:
                return cls.__getpool__(*args, **kwargs)
        except:
            obj = type.__call__(cls, *args, **kwargs)
            with cls.__instance_lock:
                cls.__setpool__(obj, *args, **kwargs)
            return obj

class SingletonPool(object):

    """Pool of singleton object.
    When using multiple inheritance, it's very advised to start to inherit
    with this class, because it's use of a metaclass overriding __call__."""

    __metaclass__ = SingletonPoolMeta

    _SingletonPoolMeta__instance_lock = Lock()
    # Can be overriden
    __instances = weakref.WeakValueDictionary()

    @staticmethod
    def __getpoolkey__(*args, **kwargs):
        return cPickle.dumps((args, kwargs))

    @classmethod
    def __getpool__(cls, *args, **kwargs):
        return cls.__instances[cls.__getpoolkey__(*args, **kwargs)]

    @classmethod
    def __setpool__(cls, obj, *args, **kwargs):
        poolkey =  cls.__getpoolkey__(*args, **kwargs)
        cls.__instances[poolkey] = obj
