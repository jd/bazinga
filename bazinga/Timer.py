import pyev
import Signal
from MainLoop import MainLoop

class Timer(pyev.Timer):

    def __init__(self, after, repeat):
        def on_timeout(*args, **kw):
            Signal.send(signal="timeout", sender=self)
        pyev.Timer.__init__(self, after, repeat, MainLoop(), on_timeout)
