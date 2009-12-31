import basic
import core.x

from xcb.xproto import *

class Window(basic.Object):

    """A basic X window."""

    def create_window(self,
            x=0, y=0, width=1, height=1, border_width=0,
            **kw):

        """Create a child window."""

        window = Window(id=core.x.Connection().connection.generate_id())

        value_mask = 0
        value_list = []

        for key, value in kw.items():
            if CW.__dict__.has_key(key):
                value_mask |= getattr(CW, key)
                value_list.append(value)

        core.x.Connection().connection.core.CreateWindow(core.x.Connection().root.root_depth,
                window.id,
                self.id,
                x, y, width, height, border_width,
                WindowClass.CopyFromParent,
                core.x.Connection().root.root_visual,
                value_mask,
                value_list)

        return window

    def map(self):

        """Map a window on screen."""

        core.x.Connection().connection.core.MapWindow(self.id)
