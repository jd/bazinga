import weakref

from . import signal as bsignal

_notify_slots = weakref.WeakValueDictionary()

class Notify(bsignal.Signal):
    """Notify signal.
    This is sent when an object see one of its attribute changed.
    On object[key] = value, Notify object is emitted on the object."""
    pass

class Object(object):
    """Base class of many bazinga objects."""

    @classmethod
    def connect_class_signal(cls, receiver, signal=bsignal.signal.All):
        """Connect a signal to all object of this class."""
        return bsignal.connect(receiver, signal=signal, sender=cls)

    @classmethod
    def disconnect_class_signal(cls, receiver, signal=bsignal.signal.All):
        """Disconnect a class signal."""
        return bsignal.disconnect(receiver, signal=signal, sender=cls)

    @classmethod
    def emit_class_signal(cls, signal=bsignal.signal.All, *args, **kw):
        """Emit a signal on all object of this class."""
        return bsignal.emit(signal, cls, *args, **kw)

    def connect_signal(self, receiver, signal=bsignal.signal.All):
        """Connect a signal."""
        return bsignal.connect(receiver, signal=signal, sender=self)

    def disconnect_signal(self, receiver, signal=bsignal.signal.All):
        """Disconnect a signal."""
        return bsignal.disconnect(receiver, signal=signal, sender=self)

    def emit_signal(self, signal=bsignal.signal.All, *args, **kw):
        """Emit a signal on an object."""
        return bsignal.emit(signal, self, *args, **kw)

    def on_signal(self, signal):
        """Return a function that can be called with a receiver as argument.
        This function will connect the receiver to the signal.
        You typically use that as a decorator:
            @object.on_signal(some_signal)
            def my_function(sender, signal):
                ..."""
        def _on_signal(func):
            self.connect_signal(func, signal)
            return func
        return _on_signal

    @staticmethod
    def get_notify(key):
        """Get the notify object corresponding to a key."""
        if not _notify_slots.has_key(key):
            notify = Notify()
            _notify_slots[key] = notify
            return notify
        return _notify_slots[key]

    def __setattr__(self, key, value):
        super(Object, self).__setattr__(key, value)
        self.emit_notify(key)

    def __delattr__(self, key):
        super(Object, self).__delattr__(key)
        self.emit_notify(key)

    def connect_notify(self, receiver, key):
        """Connect a function to a Notify signal matching key."""
        return self.connect_signal(receiver, self.get_notify(key))

    def connect_notify(self, receiver, key):
        """Disconnect a function to a Notify signal matching key."""
        return self.disconnect_signal(receiver, self.get_notify(key))

    def emit_notify(self, key):
        self.emit_signal(self.get_notify(key))

    def on_notify(self, key):
        """Return a function that can be called with a receiver as argument.
        This function will connect the receiver to the notify event matching that key.
        You typically use that as a decorator:
            @object.on_notify("some_attribute")
            def my_function(sender, signal):
                ..."""
        return self.on_signal(self.get_notify(key))
