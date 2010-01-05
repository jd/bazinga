import signal as bsignal

class Singleton(object):

    """Singleton class."""

    # The singleton instance.
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

class Setattr(bsignal.Signal):
    pass

class Object(object):

    """Base class of many bazinga objects."""

    def __init__(self, *args, **kw):

        """Initialize the object. This will copy all keywords
        arguments to the object dict."""

        self.__dict__.update(kw)


    def __setattr__(self, name, value):

        """Override setattr so it emits a signal upon attribute change.
        Note that no signal are emitted if the attribute is private (starts with _)."""

        if name[0] != "_":
            self.emit_signal(Setattr, name)
        super(Object, self).__setattr__(name, value)


    def connect_signal(self, receiver, signal=bsignal.signal.All):

        """Connect a signal."""

        return bsignal.connect(receiver, signal=signal, sender=self)


    def disconnect_signal(self, receiver, signal=bsignal.signal.All):

        """Connect a signal."""

        return bsignal.disconnect(receiver, signal=signal, sender=self)


    def emit_signal(self, signal=bsignal.signal.All, *args, **kw):

        """Emit a signal on an object."""

        return bsignal.emit(signal, self, *args, **kw)
