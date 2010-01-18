from basic import Object, Property
from x import Connection

import xcb.xproto
import inspect


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


class Window(Object):

    """A basic X window."""

    connection = Property(writable=False, type=Connection)
    xid = Property(writable=False, type=int)
    x = Property(writable=False, type=int)
    y = Property(writable=False, type=int)
    width = Property(writable=False, type=int)
    height = Property(writable=False, type=int)


    @width.writecheck
    def width_writecheck(self, value):

        if value <= 0:
            raise ValueError("Window width must be positive.")


    @height.writecheck
    def height_writecheck(self, value):

        if value <= 0:
            raise ValueError("Window width must be positive.")


    def __init__(self, xid=None, parent=None, connection=None,
                 x=0, y=0, width=1, height=1, border_width=0, **kw):

        """Create a window."""

        if xid is None:
            if parent is None:
                if connection:
                    # If creating a window with no parent, automagically pick-up first root window.
                    self.parent = connection.roots[0]
                else:
                    raise ValueError("You must provide a connection to create a window.")
            else:
                self.parent = parent
                self.connection = parent.connection
            # Generate an X id
            self.xid = self.connection.generate_id()
        else:
            self.xid = xid

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_width = border_width

        # Record everything
        Object.__init__(self, **kw)

        if xid is None:
            # XXX fix root_depth and visual
            self.connection.core.CreateWindow(self.connection.root.root_depth,
                                              self.xid,
                                              self.parent.xid,
                                              self.x, self.y, self.width, self.height,
                                              0,
                                              WindowClass.CopyFromParent,
                                              self.connection.root.root_visual,
                                              *xcb_dict_to_value(kw, xcb.xproto.CW))


    def set_events(self, events):

        """Set events that shall be received by the window."""

        self.connection.core.ChangeWindowAttributes(self.id, CW.EventMask,
                                                    events)


# Reference parent, so has to be here
Window.parent = Property(writable=False, type=Window)


class MappableWindow(Window):

    """A window that can be mapped or unmaped on screen."""

    def map(self):

        """Map a window on the screen."""

        self.connection.core.MapWindow(self.id)


    def unmap(self):

        """Unmap a window from the screen."""

        self.connection.core.UnmapWindow(self.id)


class MovableWindow(Window):

    """A window that can be moved."""

    x = Property(type=int, wcheck=Window.x.writecheck)
    y = Property(type=int, wcheck=Window.y.writecheck)


    @x.on_set
    def on_x_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id, xcb.xproto.ConfigWindow.X, [ newvalue ])


    @y.on_set
    def on_y_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id, xcb.xproto.ConfigWindow.Y, [ newvalue ])


class ResizableWindow(Window):

    """A window that can be resized."""

    width= Property(type=int, wcheck=Window.width.writecheck)
    height = Property(type=int, wcheck=Window.height.writecheck)


    @width.on_set
    def on_width_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id, xcb.xproto.ConfigWindow.Width, [ newvalue ])


    @height.on_set
    def on_height_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id, xcb.xproto.ConfigWindow.Height, [ newvalue ])


class BorderWindow(Window):

    """A window with borders."""

    border_width = Property(type=int)


    @border_width.writecheck
    def border_width_writecheck(self, value):

        if value <= 0:
            raise ValueError("Border width must be positive.")


    @border_width.on_set
    def on_border_width_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "BorderWidth": newvalue },
                                                                   xcb.xproto.ConfigWindow))
