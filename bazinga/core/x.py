import pyev
from bazinga.window import Window
from mainloop import MainLoop
from bazinga.basic import Singleton
import xcb.xproto

class Connection(Singleton, pyev.Io):

    def __init__(self, *args, **kw):
        if not hasattr(self, "connection"):
            self.connection = xcb.connect(*args, **kw)
            self.root = self.connection.get_setup().roots[0]
            pyev.Io.__init__(self, self.connection.get_file_descriptor(),
                    pyev.EV_READ, MainLoop(), Connection.on_io)

            self.screens = []
            self.screens.append(Screen(root=Window(id=self.root.root)))

    @staticmethod
    def on_io(watcher, events):
        event = watcher.connection.poll_for_event()
        print event
