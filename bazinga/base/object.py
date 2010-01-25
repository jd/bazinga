import signal as bsignal


class Object(object):
    """Base class of many bazinga objects."""

    __notify_slots = {}

    class Notify(bsignal.Signal):
        """Notify signal.
        This is sent when an object see on of its attribute changed."""
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
