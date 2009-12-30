import signal

class Singleton(object):

    """Singleton class."""

    # The singleton instance.
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

class Object(object):

    """Base class of many bazinga objects."""

    def __setattr__(self, name, value):

        """Override setattr so it emits a signal upon attribute change.
        Note that no signal are emitted if the attribute is private (starts with _)."""

        if name[0] != "_":
            signal.send(signal="setattr::%s" % name, sender=self)
        super(Object, self).__setattr__(name, value)
