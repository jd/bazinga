from base.property import cachedproperty
from base.object import Object
from x import MainConnection, byte_list_to_str
from atom import Atom
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
    xcb.xproto.FocusOutEvent: "event",
    xcb.xproto.ExposeEvent: "window",
    xcb.xproto.VisibilityNotifyEvent: "window",
    xcb.xproto.CreateNotifyEvent: "parent",
    xcb.xproto.DestroyNotifyEvent: "parent",
    xcb.xproto.UnmapNotifyEvent: "window",
    xcb.xproto.MapNotifyEvent: "window",
    xcb.xproto.MapRequestEvent: "parent",
    xcb.xproto.ReparentNotifyEvent: "window",
    xcb.xproto.ConfigureNotifyEvent: "window",
    xcb.xproto.ConfigureRequestEvent: "parent",
    xcb.xproto.GravityNotifyEvent: "window",
    xcb.xproto.CirculateNotifyEvent: "window",
    xcb.xproto.CirculateRequestEvent: "window",
    xcb.xproto.PropertyNotifyEvent: "window",
    xcb.xproto.ClientMessageEvent: "window"
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


class Window(Object):
    """A basic X window."""

    __events = xcb.xproto.EventMask.NoEvent

    class x(cachedproperty):
        """X coordinate."""
        def __get__(self):
            self._retrieve_window_geometry()

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class y(cachedproperty):
        """Y coordinate."""
        def __get__(self):
            self._retrieve_window_geometry()

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class width(cachedproperty):
        """Width."""
        def __get__(self):
            self._retrieve_window_geometry()

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class height(cachedproperty):
        """Height."""
        def __get__(self):
            self._retrieve_window_geometry()

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class _icccm_name(cachedproperty):
        """ICCCM window name."""
        def __get__(self):
            prop = MainConnection().core.GetProperty(False, self.xid,
                                                     Atom("WM_NAME"),
                                                     xcb.xproto.GetPropertyType.Any,
                                                     0, 4096).reply()
            return byte_list_to_str(prop.value)

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class _netwm_name(cachedproperty):
        """EWMH window name."""
        def __get__(self):
            prop = MainConnection().core.GetProperty(False, self.xid,
                                                     Atom("_NET_WM_NAME"),
                                                     xcb.xproto.GetPropertyType.Any,
                                                     0, 4096).reply()
            return byte_list_to_str(prop.value)

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    @property
    def name(self):
        """Window name."""
        return self._netwm_name or self._icccm_name

    def __init__(self, xid):
        self.xid = xid
        super(Window, self).__init__()

        # Receive events from the X connection
        MainConnection().connect_signal(self._dispatch_signals,
                                        signal=xcb.Event)

        # Handle ConfigureNotify to update cached attributes
        self.on_configure(self._update_window_geometry)

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
            MainConnection().core.ChangeWindowAttributes(self.xid,
                                                        xcb.xproto.CW.EventMask,
                                                        [ events ])
            self.__events = events

    def _add_event(self, event):
        """Add an event that shall be received by the window."""
        self._set_events(self.__events | event)

    def _retrieve_window_geometry(self):
        """Update window geometry."""
        wg = MainConnection().core.GetGeometry(self.xid).reply()
        Window.x.set_cache(self, wg.x)
        Window.y.set_cache(self, wg.y)
        Window.width.set_cache(self, wg.width)
        Window.height.set_cache(self, wg.height)
        return wg

    def _update_window_geometry(self, signal, sender):
        """Update window geometry from an event."""
        Window.x.set_cache(self, signal.x)
        Window.y.set_cache(self, signal.y)
        Window.width.set_cache(self, signal.width)
        Window.height.set_cache(self, signal.height)

    def focus(self):
        """Give focus to a window.
        If focus is lost, it will go back to window's parent."""
        MainConnection().core.SetInputFocus(xcb.xproto.InputFocus.Parent,
                                           self.xid,
                                           xcb.xproto.Time.CurrentTime)

    def on_enter(self, func):
        """Connect a function to a enter event."""
        self._add_event(xcb.xproto.EventMask.EnterWindow)
        self.connect_signal(func, xcb.xproto.EnterNotifyEvent)
        return func

    def on_leave(self, func):
        """Connect a function to a leave event."""
        self._add_event(xcb.xproto.EventMask.LeaveWindow)
        self.connect_signal(func, xcb.xproto.LeaveNotifyEvent)
        return func

    def on_focus(self, func):
        """Connect a function to a leave event."""
        self._add_event(xcb.xproto.EventMask.FocusChange)
        self.connect_signal(func, xcb.xproto.FocusInEvent)
        return func

    def on_unfocus(self, func):
        """Connect a function to a leave event."""
        self._add_event(xcb.xproto.EventMask.FocusChange)
        self.connect_signal(func, xcb.xproto.FocusOutEvent)
        return func

    def on_visibility(self, func):
        """Connect a function to a visibility change event."""
        self._add_event(xcb.xproto.EventMask.VisibilityChange)
        self.connect_signal(func, xcb.xproto.VisibilityNotifyEvent)
        return func

    def on_create_subwindow(self, func):
        """Connect a function to subwindow creation event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.CreateNotifyEvent)
        return func

    def on_destroy_subwindow(self, func):
        """Connect a function to a subwindow destroy event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.DestroyNotifyEvent)
        return func

    def on_map_subwindow(self, func):
        # XXX DO ME
        pass

    def on_unmap_subwindow(self, func):
        # XXX DO ME
        pass

    def on_map_subwindow_request(self, func):
        """Connect a function to a subwindow mapping request event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.MapRequestEvent)
        return func

    def on_configure(self, func):
        """Connect a function to a configure notify event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.ConfigureNotifyEvent)
        return func

    def on_configure_subwindow(self, func):
        # XXX needed?
        pass

    def on_configure_subwindow_request(self, func):
        """Connect a function to a configure request event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.ConfigureRequestEvent)
        return func

    def on_reparent(self, func):
        """Connect a function to a reparent notify event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.ReparentNotifyEvent)
        return func

    def on_reparent_subwindow(self, func):
        """Connect a function to a subwindow reparent notify event."""
        # XXX DO ME
        pass

    def on_property_change(self, func):
        """Connect a function to a reparent notify event."""
        self._add_event(xcb.xproto.EventMask.PropertyChange)
        self.connect_signal(func, xcb.xproto.PropertyNotifyEvent)
        return func


class BorderWindow(Window):
    """A window with borders."""

    class border_width(cachedproperty):
        """Border width."""
        def __get__(self):
            self._retrieve_window_geometry()

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                         xcb.xproto.ConfigWindow.BorderWidth,
                                                         [ value ])

    class border_color(cachedproperty):
        """Border color."""
        def __delete__(self):
            raise AttributeError("Border color cannot be uncached.")

        def __set__(self, value):
            color = Color(self.get_root().default_colormap, value)
            MainConnection().core.ChangeWindowAttributesChecked(self.xid,
                                                                xcb.xproto.CW.BorderPixel,
                                                                [ color.pixel ])
            return color

    def _retrieve_window_geometry(self):
        """Update window geometry."""
        wg = Window._retrieve_window_geometry(self)
        BorderWindow.border_width.set_cache(self, wg.border_width)
        return wg

    def _update_window_geometry(self, signal, sender):
        """Update window geometry from an event."""
        Window._update_window_geometry(self, signal, sender)
        BorderWindow.border_width.set_cache(self, signal.border_width)


class MappableWindow(Window):
    """A window that can be mapped or unmaped on screen."""

    def map(self):
        """Map a window on the screen."""
        MainConnection().core.MapWindow(self.xid)

    def unmap(self):
        """Unmap a window from the screen."""
        MainConnection().core.UnmapWindow(self.xid)

    def on_map(self, func):
        """Connect a function to a map event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.MapNotifyEvent)
        return func

    def on_unmap(self, func):
        """Connect a function to a unmap event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.UnmapNotifyEvent)
        return func


class MovableWindow(Window):
    """A window that can be moved."""

    class x(cachedproperty):
        __get__ = Window.x.getter

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                        xcb.xproto.ConfigWindow.X,
                                                        [ value ])
    class y(cachedproperty):
        __get__ = Window.y.getter

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                        xcb.xproto.ConfigWindow.Y,
                                                        [ value ])

class ResizableWindow(Window):
    """A window that can be resized."""

    class width(cachedproperty):
        __get__ = Window.width.getter

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                         xcb.xproto.ConfigWindow.Width,
                                                         [ value ])

    class height(cachedproperty):
        __get__ = Window.height.getter

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                        xcb.xproto.ConfigWindow.Height,
                                                        [ self.height ])


class CreatedWindow(BorderWindow, MappableWindow, MovableWindow, ResizableWindow):

    def __init__(self, connection=None, x=0, y=0, width=1, height=1,
                 border_width=0, parent=None, values={}):

        if parent is None:
            self.parent = MainConnection().roots[MainConnection().pref_screen]
        else:
            self.parent = parent

        xid = MainConnection().generate_id()

        # Always listen to this events at creation.
        # Otherwise our cache might not be up to date.
        self.__events = xcb.xproto.EventMask.StructureNotify \
                        | xcb.xproto.EventMask.PropertyChange

        create_window = \
        MainConnection().core.CreateWindowChecked(self.get_root().root_depth,
                                                 xid,
                                                 self.parent.xid,
                                                 x, y, width, height,
                                                 border_width,
                                                 xcb.xproto.WindowClass.CopyFromParent,
                                                 self.get_root().root_visual,
                                                 xcb.xproto.CW.EventMask,
                                                 [ self.__events ])

        CreatedWindow.border_width.set_cache(self, border_width)
        CreatedWindow.x.set_cache(self, x)
        CreatedWindow.y.set_cache(self, y)
        CreatedWindow.width.set_cache(self, width)
        CreatedWindow.height.set_cache(self, height)

        create_window.check()
        super(CreatedWindow, self).__init__(xid)

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

    def on_key_press(self, func):
        """Connect a function to a key press event on that window."""
        self._add_event(xcb.xproto.EventMask.KeyPress)
        self.connect_signal(func, xcb.xproto.KeyPressEvent)
        return func

    def on_key_release(self, func):
        """Connect a function to a key release event on that window."""
        self._add_event(xcb.xproto.EventMask.KeyRelease)
        self.connect_signal(func, xcb.xproto.KeyReleaseEvent)
        return func

    def on_pointer_motion(self, func):
        """Connect a function to a pointer motion."""
        self._add_event(xcb.xproto.EventMask.PointerMotion)
        self.connect_signal(func, xcb.xproto.MotionNotifyEvent)
        return func

    def on_expose(self, func):
        """Connect a function to an expose event."""
        self._add_event(xcb.xproto.EventMask.Exposure)
        self.connect_signal(func, xcb.xproto.ExposeEvent)
        return func
