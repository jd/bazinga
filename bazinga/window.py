from basic import Object, Property
import x
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


class Window(Object):

    """A basic X window."""

    connection = Property(writable=False, typecheck=x.Connection)
    xid = Property(writable=False, typecheck=int)
    parent = Property(writable=False, typecheck=Window)
    x = Property(typecheck=int)
    y = Property(typecheck=int)
    width = Property(typecheck=int)
    height = Property(typecheck=int)

    @width.writecheck
    def width_writecheck(self, value):

        if value <= 0:
            raise ValueError("Window width must be positive.")


    @height.writecheck
    def height_writecheck(self, value):

        if value <= 0:
            raise ValueError("Window width must be positive.")


    def __init__(self, xid=None, parent=None, connection=None,
                 x=0, y=0, width=1, height=1, border_width=0,
                 **kw):

        """Create a window."""

        # If creating a window with no parent, automagically pick-up first root window.
        if parent is None and wid is None:
            parent = connection.roots[0]

        if xid is None:
            xid = self.connection.generate_id()

        # XXX fix root_depth and visual
        self.connection.core.CreateWindow(self.connection.root.root_depth,
                                          window.id,
                                          self.id,
                                          x, y, width, height, border_width,
                                          WindowClass.CopyFromParent,
                                          self.connection.root.root_visual,
                                          *xcb_dict_to_value(kw, xcb.xproto.CW))

        Object.__init__(self, kw)


    def set_events(self, events):

        """Set events that shall be received by the window."""

        self.connection.core.ChangeWindowAttributes(self.id, CW.EventMask,
                                                    events)


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

    @x.on_set
    def on_x_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.ConfigureWindow(self.id,
                                            xcb_dict_to_value({ "X": newvalue },
                                                              xcb.xproto.ConfigWindow))


    @y.on_set
    def on_y_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "Y": newvalue },
                                                                   xcb.xproto.ConfigWindow))


class ResizableWindow(Window):

    """A window that can be resized."""

    @width.on_set
    def on_width_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "Width": newvalue },
                                                                   xcb.xproto.ConfigWindow))


    @height.on_set
    def on_width_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "Width": newvalue },
                                                                   xcb.xproto.ConfigWindow))


 class BorderWindow(Window):

     """A window with borders."""

    border_width = Property(typecheck=int)

    @border_width.writecheck
    def border_width_writecheck(self, value):

        if value <= 0:
            raise ValueError("Window height must be positive.")


    @border_width.on_set
    def on_border_width_set(self, oldvalue, newvalue):

        if oldvalue != None:
            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "BorderWidth": newvalue },
                                                                   xcb.xproto.ConfigWindow))
