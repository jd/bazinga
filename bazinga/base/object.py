import signal as bsignal


class Object(object):
    """Base class of many bazinga objects."""

    class New(bsignal.Signal):
        """Signal emitted on new object creation."""

    def __init__(self, *args, **kw):
        self.emit_signal(self.New)

    def connect_signal(self, receiver, signal=bsignal.signal.All):
        """Connect a signal."""
        return bsignal.connect(receiver, signal=signal, sender=self)

    def disconnect_signal(self, receiver, signal=bsignal.signal.All):
        """Disconnect a signal."""
        return bsignal.disconnect(receiver, signal=signal, sender=self)

    def emit_signal(self, signal=bsignal.signal.All, *args, **kw):
        """Emit a signal on an object."""
        return bsignal.emit(signal, self, *args, **kw)

    @classmethod
    def on_new(cls, func):
        """Decorator to connect a function to the New signal."""
        bsignal.connect(func, signal=cls.New, sender=cls)
        return func
