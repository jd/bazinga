"""Bazinga window objects."""

from base.property import cachedproperty
from base.object import Object, Notify
from base.memoize import Memoized
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
    xcb.xproto.DestroyNotifyEvent: "window",
    xcb.xproto.UnmapNotifyEvent: "window",
    xcb.xproto.MapNotifyEvent: "window",
    xcb.xproto.ReparentNotifyEvent: "window",
    xcb.xproto.ConfigureNotifyEvent: "window",
    xcb.xproto.ConfigureRequestEvent: "parent",
    xcb.xproto.GravityNotifyEvent: "window",
    xcb.xproto.CirculateNotifyEvent: "window",
    xcb.xproto.CirculateRequestEvent: "window",
    xcb.xproto.PropertyNotifyEvent: "window",
    xcb.xproto.ClientMessageEvent: "window"
}

# This event are also for a window but
# are about a subwindow
events_subwindow_attribute = {
    xcb.xproto.CreateNotifyEvent: "parent",
    xcb.xproto.DestroyNotifyEvent: "event",
    xcb.xproto.UnmapNotifyEvent: "event",
    xcb.xproto.MapNotifyEvent: "event",
    xcb.xproto.MapRequestEvent: "parent",
    xcb.xproto.ReparentNotifyEvent: "window",
    xcb.xproto.ConfigureNotifyEvent: "window",
    xcb.xproto.ConfigureRequestEvent: "parent",
    xcb.xproto.GravityNotifyEvent: "window",
    xcb.xproto.CirculateNotifyEvent: "window",
    xcb.xproto.CirculateRequestEvent: "window",
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


class _Window(Object):
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
                                                     Atom("WM_NAME").value,
                                                     xcb.xproto.GetPropertyType.Any,
                                                     0, 4096).reply()
            return byte_list_to_str(prop.value)

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    class _netwm_name(cachedproperty):
        """EWMH window name."""
        def __get__(self):
            prop = MainConnection().core.GetProperty(False, self.xid,
                                                     Atom("_NET_WM_NAME").value,
                                                     xcb.xproto.GetPropertyType.Any,
                                                     0, 4096).reply()
            return byte_list_to_str(prop.value)

        def __set__(self, value):
            raise AttributeError("read-only attribute")

    @property
    def name(self):
        """Window name."""
        return self._netwm_name or self._icccm_name

    def __init__(self, xid, parent=None):
        self.xid = xid
        self.children = []

        # Receive events from the X connection
        MainConnection().connect_signal(self._dispatch_signals,
                                        signal=xcb.Event)

        # Handle ConfigureNotify to update cached attributes
        self.on_configure(self._update_geometry)
        # Handle PropertyChange
        self.on_property_change(self._update_property)
        # Handle DestroyNotify
        self.on_destroy(self._destroy)

        # Transform and reemit some notify signals into other
        self.connect_signal(self._property_renotify, Notify)

        super(_Window, self).__init__()

        # Add to parent
        if parent:
            self.parent = parent
            # Do this last so we are sure no error happened
            parent.children.append(self)

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

    def _retrieve_geometry(self):
        """Update window geometry."""
        wg = MainConnection().core.GetGeometry(self.xid).reply()
        _Window.x.set_cache(self, wg.x)
        _Window.y.set_cache(self, wg.y)
        _Window.width.set_cache(self, wg.width)
        _Window.height.set_cache(self, wg.height)
        return wg

    def _update_geometry(self, signal, sender):
        """Update window geometry from an event."""
        _Window.x.set_cache(self, signal.x)
        _Window.y.set_cache(self, signal.y)
        _Window.width.set_cache(self, signal.width)
        _Window.height.set_cache(self, signal.height)

    def _update_property(self, signal, sender):

        # XXX move this out
        # But cannot be in class because it loop on import:
        # Window -> Atom -> x.MainConn -> Window
        _atom_to_property = {
            Atom("WM_NAME"): "_icccm_name",
            Atom("_NET_WM_NAME"): "_netwm_name",
        }
        # If this a atom property we care?
        if _atom_to_property.has_key(signal.atom):
            # Erase cache
            delattr(self, _atom_to_property[signal.atom])

    _property_renotify_map = {
        Object.get_notify("_icccm_name"): Object.get_notify("name"),
        Object.get_notify("_netwm_name"): Object.get_notify("name"),
    }

    def _property_renotify(self, sender, signal):
        """Reemit some notify events differently."""
        if self._property_renotify_map.has_key(signal):
            self.emit_signal(self._property_renotify_map[signal])

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

    def on_destroy(self, func):
        """Connect a function to a destroy event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.DestroyNotifyEvent)
        return func

    def on_destroy_subwindow(self, func):
        # XXX DO ME
        pass

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

    def destroy(self):
        """Destroy a window."""
        MainConnection().core.DestroyWindow(self.xid)

    def _destroy(self):
        """Called when a window destroy signal is received."""
        # Clear XID
        self.xid = None
        # Remove parent/child relationship
        if self.parent:
            self.parent.children.remove(self)
            del self.parent

class ExistingWindow(_Window, Memoized):
    """An already existing window."""
    pass

class BorderWindow(_Window):
    """A window with borders."""

    class border_width(cachedproperty):
        """Border width."""
        def __get__(self):
            self._retrieve_geometry()

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

    def _retrieve_geometry(self):
        """Update window geometry."""
        wg = Window._retrieve_geometry(self)
        BorderWindow.border_width.set_cache(self, wg.border_width)
        return wg

    def _update_geometry(self, signal, sender):
        """Update window geometry from an event."""
        _Window._update_geometry(self, signal, sender)
        BorderWindow.border_width.set_cache(self, signal.border_width)


class MappableWindow(_Window):
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


class MovableWindow(_Window):
    """A window that can be moved."""

    class x(cachedproperty):
        __get__ = _Window.x.getter

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                         xcb.xproto.ConfigWindow.X,
                                                         [ value ])
    class y(cachedproperty):
        __get__ = _Window.y.getter

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                         xcb.xproto.ConfigWindow.Y,
                                                         [ value ])

class ResizableWindow(_Window):
    """A window that can be resized."""

    class width(cachedproperty):
        __get__ = _Window.width.getter

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                          xcb.xproto.ConfigWindow.Width,
                                                          [ value ])

    class height(cachedproperty):
        __get__ = _Window.height.getter

        def __set__(self, value):
            MainConnection().core.ConfigureWindowChecked(self.xid,
                                                         xcb.xproto.ConfigWindow.Height,
                                                         [ self.height ])


class CreatedWindow(BorderWindow, MappableWindow, MovableWindow, ResizableWindow):

    class _icccm_name(cachedproperty):
        """ICCCM window name."""
        __get__ = _Window._icccm_name.getter

        def __set__(self, value):
            MainConnection().core.ChangeProperty(xcb.xproto.Property.NewValue,
                                                 self.xid,
                                                 Atom("WM_NAME"),
                                                 Atom("STRING"),
                                                 8, len(value), value)

    class _netwm_name(cachedproperty):
        """EWMH window name."""
        __get__ = _Window._netwm_name.getter

        def __set__(self, value):
            MainConnection().core.ChangeProperty(xcb.xproto.Property.NewValue,
                                                 self.xid,
                                                 Atom("_NET_WM_NAME").value,
                                                 Atom("STRING").value,
                                                 8, len(value), value)


    @property
    def name(self):
        """Window name."""
        return self._netwm_name or self._icccm_name

    @name.setter
    def name(self, value):
        self._icccm_name = self._netwm_name = value

    def __init__(self, parent, x=0, y=0, width=1, height=1,
                 border_width=0, values={}):

        if parent is None:
            raise

        if parent is self:
            raise

        xid = MainConnection().generate_id()

        # Always listen to this events at creation.
        # Otherwise our cache might not be up to date.
        self.__events = xcb.xproto.EventMask.StructureNotify \
                        | xcb.xproto.EventMask.SubstructureNotify \
                        | xcb.xproto.EventMask.PropertyChange


        create_window = \
        MainConnection().core.CreateWindowChecked(parent.get_root().root_depth,
                                                  xid,
                                                  parent.xid,
                                                  x, y, width, height,
                                                  border_width,
                                                  xcb.xproto.WindowClass.CopyFromParent,
                                                  parent.get_root().root_visual,
                                                  xcb.xproto.CW.EventMask,
                                                  [ self.__events ])

        CreatedWindow.border_width.set_cache(self, border_width)
        CreatedWindow.x.set_cache(self, x)
        CreatedWindow.y.set_cache(self, y)
        CreatedWindow.width.set_cache(self, width)
        CreatedWindow.height.set_cache(self, height)

        create_window.check()
        super(CreatedWindow, self).__init__(xid, parent)

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
