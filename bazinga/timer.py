import pyev
import signal
import basic
from loop import MainLoop


class Timer(basic.Object, pyev.Timer):

    class Timeout(signal.Signal):

        """Timeout signal.  This is send by the timeout object."""

        pass


    """Timer object.
    This objects send a Timeout signal every time you configure it for."""

    def __init__(self, after, repeat, loop=MainLoop()):

        """Initialize a timeout object."""

        basic.Object.__init__(self)
        pyev.Timer.__init__(self, after, repeat, loop, Timer.on_timeout)


    @staticmethod
    def on_timeout(watcher, event):

        watcher.emit_signal(signal=Timer.Timeout)
