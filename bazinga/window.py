from basic import Property
from x import Window

import xcb.xproto


class MappableWindow(Window):

    """A window that can be mapped or unmaped on screen."""

    def map(self):

        """Map a window on the screen."""

        self.connection.core.MapWindow(self.xid)


    def unmap(self):

        """Unmap a window from the screen."""

        self.connection.core.UnmapWindow(self.xid)


class MovableWindow(Window):

    """A window that can be moved."""

    x = Property(type=int, wcheck=Window.x.writecheck)
    y = Property(type=int, wcheck=Window.y.writecheck)


    @x.on_set
    def on_x_set(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.X, [ newvalue ])


    @y.on_set
    def on_y_set(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.Y, [ newvalue ])


class ResizableWindow(Window):

    """A window that can be resized."""

    width= Property(type=int, wcheck=Window.width.writecheck)
    height = Property(type=int, wcheck=Window.height.writecheck)


    @width.on_set
    def on_width_set(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.Width, [ newvalue ])


    @height.on_set
    def on_height_set(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.Height, [ newvalue ])


class BorderWindow(Window):

    """A window with borders."""

    border_width = Property(type=int)

    def __init__(self, border_width=0, **kw):

        Window.__init__(self, **kw)
        self.border_width = border_width


    @border_width.writecheck
    def border_width_writecheck(self, value):

        if value <= 0:
            raise ValueError("Border width must be positive.")


    @border_width.on_set
    def on_border_width_set(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.BorderWidth, [ newvalue ])
