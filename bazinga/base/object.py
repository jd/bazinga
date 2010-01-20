import signal as bsignal

class Object(object):

    """Base class of many bazinga objects."""

    def __init__(self, **kw):

        """Initialize the object. This will copy all keywords
        arguments to the object dict."""

        for key, value in kw.items():
            setattr(self, key, value)


    def connect_signal(self, receiver, signal=bsignal.signal.All):

        """Connect a signal."""

        return bsignal.connect(receiver, signal=signal, sender=self)


    def disconnect_signal(self, receiver, signal=bsignal.signal.All):

        """Connect a signal."""

        return bsignal.disconnect(receiver, signal=signal, sender=self)


    def emit_signal(self, signal=bsignal.signal.All, *args, **kw):

        """Emit a signal on an object."""

        return bsignal.emit(signal, self, *args, **kw)
