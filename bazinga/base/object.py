from . import signal

class Object(object):
    """Base class of many bazinga objects."""

    __notify_slots = {}

    class Notify(signal.Signal):
        """Notify signal.
        This is sent when an object see one of its attribute changed.
        On object[key] = value, Notify("key") is emitted on the object."""
        def __init__(self, value):
            self.value = value

    def connect_signal(self, receiver, signal=signal.signal.All):
        """Connect a signal."""
        return signal.connect(receiver, signal=signal, sender=self)

    def disconnect_signal(self, receiver, signal=signal.signal.All):
        """Disconnect a signal."""
        return signal.disconnect(receiver, signal=signal, sender=self)

    def emit_signal(self, signal=signal.signal.All, *args, **kw):
        """Emit a signal on an object."""
        return signal.emit(signal, self, *args, **kw)

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

    def __get_notify_slot(self, key):
        """Get the notify object corresponding to a key."""
        if not self.__notify_slots.has_key(key):
            self.__notify_slots[key] = self.Notify(key)
        return self.__notify_slots[key]

    def __setattr__(self, key, value):
        super(Object, self).__setattr__(key, value)
        self.emit_signal(self.__get_notify_slot(key))

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
