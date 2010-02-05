import cPickle

class SingletonMeta(type):
    """Singleton metaclass."""

    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except:
            cls.__instance = type.__call__(cls, *args, **kwargs)
            return cls.__instance


class Singleton(object):
    """Singleton class."""

    __metaclass__ = SingletonMeta


class SingletonPoolMeta(type):
    """Singleton pool metaclass."""

    def __call__(cls, *args, **kwargs):
        try:
            key = cls.__getpool__(*args, **kwargs)
            return key
        except:
            obj = type.__call__(cls, *args, **kwargs)
            cls.__setpool__(obj, *args, **kwargs)
            return obj


class SingletonPool(object):

    """Pool of singleton object.
    When using multiple inheritance, it's very advised to start to inherit
    with this class, because it's use of a metaclass overriding __call__."""

    __metaclass__ = SingletonPoolMeta

    @staticmethod
    def __getpoolkey__(*args, **kwargs):
        return cPickle.dumps((args, kwargs))

    @classmethod
    def __getpool__(cls, *args, **kwargs):
        return cls.__instances[cls.__getpoolkey__(*args, **kwargs)]

    @classmethod
    def __setpool__(cls, obj, *args, **kwargs):
        cls.__instances[cls.__getpoolkey__(*args, **kwargs)] = obj
