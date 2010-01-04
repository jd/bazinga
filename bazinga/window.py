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

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_width = border_width

        return window

    def move_resize(self, x, y, width, height):

        """Move or resize a window."""

        value_mask = 0
        value_list = []

        if self.movable:
            if x != self.x
                value_mask |= ConfigWindow.X
                value_list.append(x)
            if y != self.y:
                value_mask |= ConfigWindow.Y
                value_list.append(y)

        if self.resizable:
            if width != self.width:
                value_mask |= ConfigWindow.Width
                value_list.append(width)
            if height != self.height:
                value_mask |= ConfigWindow.Height
                value_list.append(height)

        if value_mask:
            core.x.Connection().connection.ConfigureWindow(self.id, value_mask, value_list)


    def move(self, x, y)
        
        """Move a aindow"""

        self.move_resize(x, y, self.width, self.height)


    def resize(self, width, height)

        """Resize a window"""

        self.move_resize(self.x, self.y, width, height)


    def map(self):

        """Map a window on screen."""

        core.x.Connection().connection.core.MapWindow(self.id)

    def unmap(self):

        """Unmap a window on screen."""

        core.x.Connection().connection.core.UnmapWindow(self.id)
