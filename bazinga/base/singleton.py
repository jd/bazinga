from threading import Lock

class SingletonMeta(type):
    """Singleton metaclass."""

    def __call__(cls, *args, **kwargs):
        obj, do_init = cls.__new__(cls, *args, **kwargs)
        if obj and do_init:
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
