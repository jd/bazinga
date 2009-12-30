import pyev
from mainloop import MainLoop
from bazinga.basic import Singleton
import xcb, xcb.xproto

class Connection(Singleton, pyev.Io):

    def __init__(self, *args, **kw):
        if not hasattr(self, "connection"):
            self.connection = xcb.connect(*args, **kw)
            pyev.Io.__init__(self, self.connection.get_file_descriptor(),
                    pyev.EV_READ, MainLoop(), X.on_io, self)

    @staticmethod
    def on_io(watcher, events):
        event = watcher.data.poll_for_event()
        print event
