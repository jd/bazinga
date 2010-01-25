from . import signal as bsignal

class Object(object):
    """Base class of many bazinga objects."""

    __notify_slots = {}

    class Notify(bsignal.Signal):
        """Notify signal.
        This is sent when an object see one of its attribute changed.
        On object[key] = value, Notify("key") is emitted on the object."""
        def __init__(self, value):
            self.value = value

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

    @classmethod
    def __get_notify_slot(cls, key):
        """Get the notify object corresponding to a key."""
        if not cls.__notify_slots.has_key(key):
            cls.__notify_slots[key] = cls.Notify(key)
        return cls.__notify_slots[key]

    def _emit_notify(self, key):
        # Do not emit signal on private attributes
        if len(key) > 0 and key[0] != "_":
            self.emit_signal(self.__class__.__get_notify_slot(key))

    def __setattr__(self, key, value):
        super(Object, self).__setattr__(key, value)
        self._emit_notify(key)

    def __delattr__(self, key):
        super(Object, self).__delattr__(key)
        self._emit_notify(key)

    def connect_notify(self, receiver, key):
        """Connect a function to a Notify signal matching key."""
        return self.connect_signal(receiver, self.__get_notify_slot(key))

    def on_notify(self, key):
        """Return a function that can be called with a receiver as argument.
        This function will connect the receiver to the notify event matching that key.
        You typically use that as a decorator:
            @object.on_notify("some_attribute")
            def my_function(sender, signal):
                ..."""
        return self.on_signal(self.__get_notify_slot(key))
