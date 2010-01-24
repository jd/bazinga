from base.property import cachedproperty
import base.signal as signal
from x import XObject
import color

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

    __events = xcb.xproto.EventMask.NoEvent

    class x(cachedproperty):
        """X coordinate."""
        def __get__(self):
            return 42

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class y(cachedproperty):
        """Y coordinate."""
        def __get__(self):
            return 43

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class width(cachedproperty):
        """Width."""
        def __get__(self):
            return 42

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class height(cachedproperty):
        """Height."""
        def __get__(self):
            return 42

        def __set__(self, value):
            raise AttributeError("read-only attribute")


    def __init__(self, connection, xid):
        self.xid = xid
        super(Window, self).__init__(connection)

        # Receive events from the X connection
        self.connection.connect_signal(self._dispatch_signals,
                                       signal=xcb.Event)

    # XXX Should be cached?
    def get_root(self):
        """Get the root window the window is attached on."""
        try:
            while self.parent:
                self = self.parent
        except AttributeError:
            # No parent
            pass
        return self

    def _is_event_for_me(self, event):
        """Guess if an X even is for us or not."""

        if event.__class__ in events_window_attribute.keys():
            return getattr(event, events_window_attribute[event.__class__]) == self.xid
        return False

    def _dispatch_signals(self, signal, sender):
        """Dipatch signals that belongs to us."""

        if self._is_event_for_me(signal):
            self.emit_signal(signal)

    def on_event(self, func):
        """Connect a function to any event."""
        self.connect_signal(func, xcb.Event)
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


class BorderWindow(Window):
    """A window with borders."""

    class border_width(cachedproperty):
        """Border width."""
        def __get__(self):
            return 100

        def __set__(self, value):
            self.connection.core.ConfigureWindowChecked(self.xid,
                                                        xcb.xproto.ConfigWindow.BorderWidth,
                                                        [ value ]).check()

    class border_color(cachedproperty):
        """Border color."""
        def __get__(self):
            return 100

        def __set__(self, value):
            if isinstance(value, color.Color):
                bcolor = value
            else:
                bcolor = color.make_color(self.get_root().default_colormap, value)
            self.connection.core.ChangeWindowAttributesChecked(self.xid,
                                                               xcb.xproto.CW.BorderPixel,
                                                               [ bcolor.pixel ]).check()
            return bcolor


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

    class x(cachedproperty):
        __get__ = Window.x.getter

        def __set__(self, value):
            self.connection.core.ConfigureWindowChecked(self.xid,
                                                        xcb.xproto.ConfigWindow.X,
                                                        [ value ]).check()
    class y(cachedproperty):
        __get__ = Window.y.getter

        def __set__(self, value):
            self.connection.core.ConfigureWindowChecked(self.xid,
                                                        xcb.xproto.ConfigWindow.Y,
                                                        [ value ]).check()

class ResizableWindow(Window):
    """A window that can be resized."""

    class width(cachedproperty):
        __get__ = Window.width.getter

        def __set__(self, value):
            self.connection.core.ConfigureWindowChecked(self.xid,
                                                         xcb.xproto.ConfigWindow.Width,
                                                         [ value ]).check()

    class height(cachedproperty):
        __get__ = Window.height.getter

        def __set__(self, value):
            self.connection.core.ConfigureWindowChecked(self.xid,
                                                        xcb.xproto.ConfigWindow.Height,
                                                        [ self.height ]).check()


class CreatedWindow(BorderWindow, MappableWindow, MovableWindow, ResizableWindow):

    def __init__(self, connection=None, x=0, y=0, width=1, height=1,
                 border_width=0, parent=None, values={}):

        # Build self.connection
        XObject.__init__(self, connection)

        if parent is None:
            self.parent = self.connection.roots[self.connection.pref_screen]
        else:
            self.parent = parent

        xid = self.connection.generate_id()

        create_window = \
        self.connection.core.CreateWindowChecked(self.get_root().root_depth,
                                                 xid,
                                                 self.parent.xid,
                                                 x, y, width, height,
                                                 border_width,
                                                 xcb.xproto.WindowClass.CopyFromParent,
                                                 self.get_root().root_visual,
                                                 *xcb_dict_to_value(values, xcb.xproto.CW))
        CreatedWindow.border_width.set_cache(self, border_width)
        CreatedWindow.x.set_cache(self, x)
        CreatedWindow.y.set_cache(self, y)
        CreatedWindow.width.set_cache(self, width)
        CreatedWindow.height.set_cache(self, height)

        create_window.check()
        super(CreatedWindow, self).__init__(connection, xid)


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
