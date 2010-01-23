from base.property import Property
import base.signal as signal
from x import XObject
from color import Color

import xcb.xproto

events_window_attribute = {
    xcb.xproto.KeyPressEvent: "event",
    xcb.xproto.KeyReleaseEvent: "event",
    xcb.xproto.ButtonPressEvent: "event",
    xcb.xproto.ButtonReleaseEvent: "event",
    xcb.xproto.MotionNotifyEvent: "event",
    xcb.xproto.EnterNotifyEvent: "event",
    xcb.xproto.LeaveNotifyEvent: "event",
    xcb.xproto.FocusInEvent: "event",
    xcb.xproto.ExposeEvent: "window",
    xcb.xproto.GraphicsExposureEvent: "drawable",
    xcb.xproto.NoExposureEvent: "drawable",
    xcb.xproto.VisibilityNotifyEvent: "window",
    xcb.xproto.CreateNotifyEvent: "window",
    xcb.xproto.DestroyNotifyEvent: "window",
    xcb.xproto.UnmapNotifyEvent: "window",
    xcb.xproto.MapNotifyEvent: "window",
    xcb.xproto.MapRequestEvent: "window",
    xcb.xproto.ReparentNotifyEvent: "window",
    xcb.xproto.ConfigureNotifyEvent: "window",
    xcb.xproto.ConfigureRequestEvent: "window",
    xcb.xproto.GravityNotifyEvent: "window",
    xcb.xproto.ResizeRequestEvent: "window",
    xcb.xproto.CirculateNotifyEvent: "window",
    xcb.xproto.CirculateRequestEvent: "window",
    xcb.xproto.PropertyNotifyEvent: "window",
    xcb.xproto.PropertyNotifyEvent: "window"
}


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
    __events = xcb.xproto.EventMask.NoEvent

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

        # Receive events from the X connection
        self.connection.connect_signal(self._dispatch_signals,
                                       signal=xcb.Event)

    def get_root(self):
        """Get the root window the window is attached on."""

        while self.parent:
            self = self.parent

        return self

    def _is_event_for_me(self, event):
        """Guess if an X even is for us or not."""

        if event.__class__ in events_window_attribute.keys():
            return getattr(event, events_window_attribute[event.__class__]) == self.xid
        return False


    def _dispatch_signals(self, event, signal, sender):
        """Dipatch signals that belongs to us."""

        if self._is_event_for_me(event):
            self.emit_signal(event, event)

    def on_event(self, func):
        """Connect a function to any event."""
        self.connect_signal(func, xcb.Event)
        return func

    def on_button_press(self, func):
        """Connect a function to a button press event on that window."""
        self._add_event(xcb.xproto.EventMask.ButtonPress)
        self.connect_signal(func, xcb.xproto.ButtonPressEvent)
        return func

    def on_button_release(self, func):
        """Connect a function to a button release event on that window."""
        self._add_event(xcb.xproto.EventMask.ButtonRelease)
        self.connect_signal(func, xcb.xproto.ButtonReleaseEvent)
        return func

    def _set_events(self, events):
        """Set events that shall be received by the window."""

        if events != self.__events:
            self.connection.core.ChangeWindowAttributes(self.xid,
                                                        xcb.xproto.CW.EventMask,
                                                        [ events ])
            self.__events = events

    def _add_event(self, event):
        """Add an event that shall be received by the window."""

        self._set_events(self.__events | event)


# Reference Window, so has to be here
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
