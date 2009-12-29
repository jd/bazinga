import pyev
from MainLoop import MainLoop

class X(pyev.Io):
    def __init__(self, display=None):
        self.connection = xcb.connect(disaply)
        pyev.Io.__init__(self, self.connection.get_file_descriptor(), MainLoop(), on_io, self)

    def on_io(watcher, events):
        #watcher.data.poll_for_event()
        pass
