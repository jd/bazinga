import pyev
import base.signal as signal
from base.object import Object
from loop import MainLoop


class Timer(Object, pyev.Timer):
    class Timeout(signal.Signal):
        """Timeout signal.  This is send by the timeout object."""
        pass

    """Timer object.
    This object sends a Timeout signal every time you configure it for."""

    def __init__(self, after, repeat, loop=None):
        """Initialize a timeout object."""
        if loop is None:
            loop = MainLoop()
        super(Timer, self).__init__(after, repeat, loop, Timer._on_timeout)


    @staticmethod
    def _on_timeout(watcher, event):
        watcher.emit_signal(signal=Timer.Timeout)

    def on_timeout(self, func):
        """Connect a function to the timer timeout."""
        self.connect_signal(func, self.Timeout)
        return func
