import signal as bsignal
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


class Setattr(bsignal.Signal):
    pass


class Object(object):

    """Base class of many bazinga objects."""

    def __init__(self, **kw):

        """Initialize the object. This will copy all keywords
        arguments to the object dict."""

        for key, value in kw.items():
            setattr(self, key, value)


    def __setattr__(self, name, value):

        """Override setattr so it emits a signal upon attribute change.
        Note that no signal are emitted if the attribute is private (starts with _)."""

        # If attribute is not private (starts with _)
        if name[0] != "_":
            if hasattr(self, name):
                # Get old value
                oldvalue = getattr(self, name)
            else:
                oldvalue = None

            # Be smart.
            if oldvalue != value:

                # If the object a __setattr_name method, call it.
                setter_name = "__setattr_%s__" % name
                if hasattr(self, setter_name):
                    getattr(self, setter_name)(oldvalue, value)

                # Emit a signal to indicate a change to the user.
                self.emit_signal(Setattr, name, oldvalue, value)

        # Store new value.
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
