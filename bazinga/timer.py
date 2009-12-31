import pyev
import signal
import basic
from core.mainloop import MainLoop

class Timeout(signal.Signal):
    pass

class Timer(basic.Object, pyev.Timer):

    def __init__(self, after, repeat):
        basic.Object.__init__(self)
        pyev.Timer.__init__(self, after, repeat, MainLoop(), Timer.on_timeout)

    @staticmethod
    def on_timeout(watcher, event):
        watcher.emit_signal(signal=Timeout, sender=watcher)
