import basic
import core.x

from xcb.xproto import *

# Iterate over values
# CW has .BackingPixel = 4096,
# So we build 4096 = BackingPixel, sort keys and then iterate.
CW_rev = dict(zip(CW.__dict__.values(), CW.__dict__.keys()))
CW_keys = CW_rev.keys()
CW_keys.sort()

class Window(basic.Object):

    """A basic X window."""

    def create_window(self,
            x=0, y=0, width=1, height=1, border_width=0,
            window_class=WindowClass.CopyFromParent,
            values={}):

        """Create a child window."""

        window = Window(id=core.x.Connection().connection.generate_id())

        value_mask = 0
        value_list = []
        for mask in CW_keys:
            if mask and values.has_key(CW_rev[mask]):
                value_mask |= mask
                value_list.append(values[CW_rev[mask]])

        core.x.Connection().connection.core.CreateWindow(core.x.Connection().root.root_depth,
                window.id,
                self.id,
                x, y, width, height, border_width,
                window_class,
                core.x.Connection().root.root_visual,
                value_mask,
                value_list)

        return window

    def map(self):

        """Map a window on screen."""

        core.x.Connection().connection.core.MapWindow(self.id)
