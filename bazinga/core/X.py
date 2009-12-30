import pyev
from MainLoop import MainLoop
import xcb, xcb.xproto

class X(pyev.Io):

    def __init__(self, *args, **kw):
        connection = xcb.connect(*args, **kw)
        pyev.Io.__init__(self, connection.get_file_descriptor(), MainLoop(), on_io, self)

    def on_io(watcher, events):
        #watcher.data.poll_for_event()
        pass
