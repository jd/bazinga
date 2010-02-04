from . import signal as bsignal
from singleton import SingletonPool

class Notify(SingletonPool):
    """Notify signal.
    This is sent when an object see one of its attribute changed.
    On object[key] = value, Notify object is emitted on the object."""

    def __init__(self, attribute):
        self.attribute = attribute


class Object(object):
    """Base class of many bazinga objects."""

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

    connect_class_signal = classmethod(connect_signal)
    disconnect_class_signal = classmethod(disconnect_signal)
    emit_class_signal = classmethod(emit_signal)

    @classmethod
    def on_class_signal(cls, signal):
        """Return a function that can be called with a receiver as argument.
        This function will connect the receiver to the signal.
        You typically use that as a decorator:
            @MyClass.on_class_signal(some_signal)
            def my_function(sender, signal):
                ..."""
        def _on_signal(func):
            cls.connect_class_signal(func, signal)
            return func
        return _on_signal

    def __setattr__(self, key, value):
        super(Object, self).__setattr__(key, value)
        self.emit_notify(key)

    def __delattr__(self, key):
        super(Object, self).__delattr__(key)
        self.emit_notify(key)

    def connect_notify(self, receiver, key):
        """Connect a function to a Notify signal matching key."""
        return self.connect_signal(receiver, Notify(key))

    def disconnect_notify(self, receiver, key):
        """Disconnect a function to a Notify signal matching key."""
        return self.disconnect_signal(receiver, Notify(key))

    def emit_notify(self, key):
        self.emit_signal(Notify(key))

    def on_notify(self, key):
        """Return a function that can be called with a receiver as argument.
        This function will connect the receiver to the notify event matching that key.
        You typically use that as a decorator:
            @object.on_notify("some_attribute")
            def my_function(sender, signal):
                ..."""
        return self.on_signal(Notify(key))

    connect_class_notify = classmethod(connect_notify)
    disconnect_class_notify = classmethod(disconnect_notify)
    emit_class_notify = classmethod(emit_notify)

    def on_class_notify(cls, key):
        """Return a function that can be called with a receiver as argument.
        This function will connect the receiver to the notify event matching that key.
        You typically use that as a decorator:
            @MyClass.on_notify("some_attribute")
            def my_function(sender, signal):
                ..."""
        return cls.on_class_signal(Notify(key))
