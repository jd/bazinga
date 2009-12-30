import pyev
import signal
from core.mainloop import MainLoop

class Timer(pyev.Timer):

    def __init__(self, after, repeat):
        pyev.Timer.__init__(self, after, repeat, MainLoop(), Timer.on_timeout, self)

    @staticmethod
    def on_timeout(watcher, event):
        Signal.send(signal="timeout", sender=watcher.data)
