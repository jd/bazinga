import pyev
from mainloop import MainLoop
from bazinga.basic import Singleton
import xcb
from xcb.xproto import *
from window import Window

# Iterate over values
# CW has .BackingPixel = 4096,
# So we build 4096 = BackingPixel, sort keys and then iterate.
CW_rev = dict(zip(CW.__dict__.values(), CW.__dict__.keys()))
CW_keys = a.keys()
CW_keys.sort()

class Connection(Singleton, pyev.Io):

    def __init__(self, *args, **kw):
        if not hasattr(self, "connection"):
            self.connection = xcb.connect(*args, **kw)
            self.root = self.connect.get_setup().roots[0]
            pyev.Io.__init__(self, self.connection.get_file_descriptor(),
                    pyev.EV_READ, MainLoop(), X.on_io, self)

    @staticmethod
    def on_io(watcher, events):
        event = watcher.data.poll_for_event()
        print event

    def flush(self):
        self.connection.flush()

    def create_window(self, parent=root.root,
            x=0, y=0, width=1, height=1, border_width=0,
            window_class=WindowClass.CopyFromParent,
            values={})
        window = Window(self.connection.generate_id())

        value_mask = 0
        value_list = []
        for mask in CW_keys:
            if hasattr(values, CW_rev[mask]):
                value_mask |= mask
                value_list.append(values[CW_rev[mask]])

        self.connection.core.CreateWindow(self.root.root_depth,
                window.id,
                parent,
                x, y, width, height, border_width,
                window_class,
                root.root_visual,
                value_mask,
                value_list)

        return window
