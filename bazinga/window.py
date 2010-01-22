from base.property import Property
from x import XObject
from color import Color

import xcb.xproto


def xcb_dict_to_value(values, xcb_dict):

    """Many X values are made from a mask indicating which values are present
    in the request and the actual values. We use that function to build this two
    variables from a dict { OverrideRedirect: 1 }
    to a mask |= OverrideRedirect and value = [ 1 ]"""

    value_mask = 0
    value_list = []

    xcb_dict_rev = dict(zip(xcb_dict.__dict__.values(),
                            xcb_dict.__dict__.keys()))
    xcb_dict_keys = xcb_dict_rev.keys()
    xcb_dict_keys.sort()

    for mask in xcb_dict_keys:
        if mask and values.has_key(xcb_dict_rev[mask]):
            value_mask |= mask
            value_list.append(values[xcb_dict_rev[mask]])

    return value_mask, value_list


class Window(XObject):

    """A basic X window."""

    xid = Property("The X id of the object.", writable=False, type=int)
    x = Property("x coordinate.", writable=False, type=int)
    y = Property("y coordinate.", writable=False, type=int)
    width = Property("Width.", writable=False, type=int)
    height = Property("Height.", writable=False, type=int)


    @width.writecheck
    def _writcheck_width(self, value):

        if value <= 0:
            raise ValueError("Window width must be positive.")


    @height.writecheck
    def _writecheck_height(self, value):

        if value <= 0:
            raise ValueError("Window width must be positive.")


    def __init__(self, xid=None, parent=None, x=0, y=0, width=1, height=1, **kw):

        """Create a window."""

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Record everything else
        XObject.__init__(self, **kw)

        if xid is None:
            # Generate an X id
            self.xid = self.connection.generate_id()
            if parent is None:
                parent = self.connection.roots[self.connection.pref_screen]
        else:
            if parent is not None and  parent.connection != self.connection:
                raise ValueError("Parent connection should be the same")
            self.xid = xid

        if parent:
            self.parent = parent

        if xid is None:
            self.connection.core.CreateWindow(self.get_root().root_depth,
                                              self.xid,
                                              self.parent.xid,
                                              self.x, self.y, self.width, self.height,
                                              0,
                                              xcb.xproto.WindowClass.CopyFromParent,
                                              self.get_root().root_visual,
                                              *xcb_dict_to_value(kw, xcb.xproto.CW))


    def get_root(self):

        """Get the root window the window is attached on."""

        while self.parent:
            self = self.parent

        return self


    def set_events(self, events):

        """Set events that shall be received by the window."""

        self.connection.core.ChangeWindowAttributes(self.xid, CW.EventMask, events)


# Reference parent, so has to be here
Window.parent = Property("Parent window.", writable=False, type=Window)


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

    x = Property(Window.x.__doc__, type=int, wcheck=Window.x.writecheck)
    y = Property(Window.y.__doc__, type=int, wcheck=Window.y.writecheck)


    @x.on_set
    def _on_set_x(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.X, [ newvalue ])


    @y.on_set
    def _on_set_y(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.Y, [ newvalue ])


class ResizableWindow(Window):

    """A window that can be resized."""

    width = Property(Window.width.__doc__, type=int, wcheck=Window.width.writecheck)
    height = Property(Window.height.__doc__, type=int, wcheck=Window.height.writecheck)


    @width.on_set
    def _on_set_width(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.Width, [ newvalue ])


    @height.on_set
    def _on_set_height(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.Height, [ newvalue ])


class BorderWindow(Window):

    """A window with borders."""

    border_width = Property("The window border width.", type=int)
    border_color = Property("The window border color.", type=Color)

    def __init__(self, border_width=0, **kw):

        Window.__init__(self, **kw)
        self.border_width = border_width


    @border_width.writecheck
    def _writecheck_border_width(self, value):

        if value <= 0:
            raise ValueError("Border width must be positive.")


    @border_width.on_set
    def _on_set_border_width(self, newvalue):

        self.connection.core.ConfigureWindow(self.xid, xcb.xproto.ConfigWindow.BorderWidth, [ newvalue ])

    @border_color.on_set
    def _on_set_border_color(self, newvalue):

        self.connection.core.ChangeWindowAttributes(self.xid, xcb.xproto.CW.BorderPixel, [ newvalue.pixel ])
