from louie import *
from decorator import decorator

def emit(signal=signal.All, sender=sender.Anonymous, *arguments, **named):

    """Emit a signal. This is the same as send, except that it also emit the
    signal on object classes, following MRO."""

    ret = []
    for s in [ sender ] + list(sender.__class__.__mro__):
        ret += send(signal, s, *arguments, **named)
    return ret


def connected(signal=signal.All, sender=sender.Any, weak=True):

    """Return a decorator function that will connect
    the underlying function to an event."""

    @decorator
    def connect_func(func):
        connect(func, signal, sender)
        return func

    return connect_func
