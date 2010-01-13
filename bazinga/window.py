import basic
import xcb.xproto


class NotResizable(Exception):
    pass


class NotMovable(Exception):
    pass


class NoBorder(Exception):
    pass


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


class Window(basic.Object):

    """A basic X window."""

    def create_window(self,
                      x=0, y=0, width=1, height=1, border_width=0,
                      movable=True, resizable=True, noborder=False,
                      **kw):

        """Create a child window."""

        window = Window(id = self.connection.generate_id(),
                        x = x,
                        y = y,
                        width = width,
                        height = height,
                        border_width = border_width,
                        movable = movable,
                        resizable = resizable,
                        noborder = noborder,
                        connection = self.connection,
                        parent = self)

        # XXX fix root_depth and visual
        self.connection.core.CreateWindow(self.connection.root.root_depth,
                                          window.id,
                                          self.id,
                                          x, y, width, height, border_width,
                                          WindowClass.CopyFromParent,
                                          self.connection.root.root_visual,
                                          *xcb_dict_to_value(kw, xcb.xproto.CW))

        return window


    def set_events(self, events):

        """Set events that shall be received by the window."""

        self.connection.core.ChangeWindowAttributes(self.id, CW.EventMask,
                                                    events)


    @property
    def connection(self):

        return self._connection

    @connection.setter
    def connection(self, value):

        if hasattr(self, "_connection"):
            raise ValueError("cannot change window connection")

    connection = property(lambda self: return self._connection,
                          lambda self, value:


    def __setattr_id__(self, oldvalue, newvalue):

        if oldvalue != None:
            raise ValueError("cannot change window id")


    def __setattr_x__(self, oldvalue, newvalue):

        if oldvalue != None:
            if not self.movable:
                raise NotMovable

            self.connection.ConfigureWindow(self.id,
                                            xcb_dict_to_value({ "X": newvalue },
                                                              xcb.xproto.ConfigWindow))


    def __setattr_y__(self, oldvalue, newvalue):

        if oldvalue != None:
            if not self.movable:
                raise NotMovable

            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "Y": newvalue },
                                                                   xcb.xproto.ConfigWindow))


    def __setattr_width__(self, oldvalue, newvalue):

        if oldvalue != None:
            if newvalue <= 0:
                raise ValueError("Window width must be positive.")

            if not self.resizable:
                raise NotResizable

            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "Width": newvalue },
                                                                   xcb.xproto.ConfigWindow))


    def __setattr_height__(self, oldvalue, newvalue):

        if oldvalue != None:
            if newvalue <= 0:
                raise ValueError("Window height must be positive.")

            if not self.resizable:
                raise NotResizable

            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "Height": newvalue },
                                                                   xcb.xproto.ConfigWindow))


    def __setattr_border_width__(self, oldvalue, newvalue):

        if oldvalue != None:
            if self.noborder:
                raise NoBorder("This window cannot have border.")

            if newvalue <= 0:
                raise ValueError("Window height must be positive.")

            self.connection.core.ConfigureWindow(self.id,
                                                 xcb_dict_to_value({ "BorderWidth": newvalue },
                                                                   xcb.xproto.ConfigWindow))


    def map(self):

        """Map a window on the screen."""

        self.connection.core.MapWindow(self.id)


    def unmap(self):

        """Unmap a window from the screen."""

        self.connection.core.UnmapWindow(self.id)
