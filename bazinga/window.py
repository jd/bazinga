import basic
import xcb.xproto

def xcb_dict_to_value(values, xcb_dict):

    """Many X values are made from a mask indicating which values are present
    in the request and the actual values. We use that function to build this two
    variables from a dict { OverrideRedirect: 1 }
    to a mask |= OverrideRedirect and value = [ 1 ]"""

    value_mask = 0
    value_list = []

    xcb_dict_rev = dict(zip(xcb_dict.__dict__.values(), xcb_dict.__dict__.keys()))
    xcb_dict_keys = xcb_dict_rev.keys()
    xcb_dict_keys.sort()

    for mask in xcb_dict_keys:
        if mask and values.has_key(xcb_dict_rev[mask]):
            value_mask |= mask
            value_list.append(values[CW_rev[mask]])

    return value_mask, value_list


class Window(basic.Object):

    """A basic X window."""

    def create_window(self,
            x=0, y=0, width=1, height=1, border_width=0,
            **kw):

        """Create a child window."""

        window = Window(id=self.connection.connection.generate_id())

        # XXX fix root_depth and visual
        self.connection.connection.core.CreateWindow(self.connection.connection.root.root_depth,
                window.id,
                self.id,
                x, y, width, height, border_width,
                WindowClass.CopyFromParent,
                self.connection.connection.root.root_visual,
                *xcb_dict_to_value(kw, xcb.xproto.CW))

        window.connection = self.connection
        window.x = x
        window.y = y
        window.width = width
        window.height = height
        window.border_width = border_width

        return window

    def set_events(self, **kw):

        """Set events that shall be received by the window."""

        self.connection.connection.core.ChangeWindowAttributes(
                self.id,
                *xcb_dict_to_value(kw, xcb.xproto.CW))


    def __setattr_x(self, oldvalue, newvalue):

        self.connection.connection.ConfigureWindow(self.id, xcb_dict_to_value({ X: newvalue }, xcb.xproto.ConfigWindow))


    def __setattr_y(self, oldvalue, newvalue):

        self.connection.connection.ConfigureWindow(self.id, xcb_dict_to_value({ Y: newvalue }, xcb.xproto.ConfigWindow))


    def __setattr_width(self, oldvalue, newvalue):

        self.connection.connection.ConfigureWindow(self.id, xcb_dict_to_value({ Width: newvalue }, xcb.xproto.ConfigWindow))


    def __setattr_height(self, oldvalue, newvalue):

        self.connection.connection.ConfigureWindow(self.id, xcb_dict_to_value({ Height: newvalue }, xcb.xproto.ConfigWindow))


    def map(self):

        """Map a window on the screen."""

        self.connection.connection.core.MapWindow(self.id)


    def unmap(self):

        """Unmap a window from the screen."""

        self.connection.connection.core.UnmapWindow(self.id)
