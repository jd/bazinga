import pyev
import signal
import basic
from core.mainloop import MainLoop

class Timer(basic.Object, pyev.Timer):

    def __init__(self, after, repeat):
        pyev.Timer.__init__(self, after, repeat, MainLoop(), Timer.on_timeout, self)

    @staticmethod
    def on_timeout(watcher, event):
        signal.send(signal="timeout", sender=watcher.data)
