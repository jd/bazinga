from louie import *

def emit(signal=signal.All, sender=sender.Anonymous, *arguments, **named):

    """Emit a signal. This is the same as send, except that it also emit the
    signal on object classes, following MRO."""

    ret = []
    for s in [ sender ] + list(sender.__class__.__mro__):
        ret += send(signal, s, *arguments, **named)
    return ret
