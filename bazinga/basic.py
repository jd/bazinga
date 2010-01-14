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


class Object(object):

    """Base class of many bazinga objects."""

    class Setattr(bsignal.Signal):

        pass


    def __init__(self, **kw):

        """Initialize the object. This will copy all keywords
        arguments to the object dict."""

        for key, value in kw.items():
            setattr(self, key, value)


    def __setattr__(self, name, value):

        """Override setattr so it emits a signal upon attribute change.
        Note that no signal are emitted if the attribute is private (starts with _)."""

        # Store new value.
        super(Object, self).__setattr__(name, value)

        # If attribute is not private (starts with _)
        if name[0] != "_":
            if hasattr(self, name):
                # Get old value
                oldvalue = getattr(self, name)
            else:
                oldvalue = None

            # Be smart.
            if oldvalue != value:
                # Emit a signal to indicate a change to the user.
                self.emit_signal(Setattr, name, oldvalue, value)


    def connect_signal(self, receiver, signal=bsignal.signal.All):

        """Connect a signal."""

        return bsignal.connect(receiver, signal=signal, sender=self)


    def disconnect_signal(self, receiver, signal=bsignal.signal.All):

        """Connect a signal."""

        return bsignal.disconnect(receiver, signal=signal, sender=self)


    def emit_signal(self, signal=bsignal.signal.All, *args, **kw):

        """Emit a signal on an object."""

        return bsignal.emit(signal, self, *args, **kw)


class Property(Object):

    """A property object."""

    class Set(bsignal.Signal):

        pass


    def __init__(self, default_value=None, readable=True, writable=True, deletable=False, wcheck=None):

        self.wcheck = wcheck
        self.readable = readable
        self.writable = writable
        self.deletable = deletable
        self.default_value = default_value
        self.values = {}


    def __get__(self, inst, owner=None):

        if inst is None:
            return self
        if not self.readable:
            raise AttributeError("unreadable attribute")
        if self.values.has_key(inst):
            return self.values[inst]
        return self.default_value


    def __set__(self, inst, value):

        # Do not block initial set
        if self.values.has_key(inst):
            if not self.writable:
                raise AttributeError("unwritable attribute")
        if self.wcheck:
            self.wcheck(inst, value)
        if self.values.has_key(inst):
            oldvalue = self.values[inst]
        else:
            oldvalue = self.default_value
        self.values[inst] = value
        self.emit_signal(self.Set, inst, oldvalue, value)


    def __delete__(self, inst):

        if not self.deletable:
            raise AttributeError("undeletable attribute")
        del self.values[inst]


    def writecheck(self, func):

        self.wcheck = func
        return self


    def on_set(self, func):

        self.connect_signal(func, self.Set)
        return func
