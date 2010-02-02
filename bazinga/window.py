"""Bazinga window objects."""

from base.property import cachedproperty, rocachedproperty
from base.object import Object, Notify
from base.singleton import SingletonPool
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
    xcb.xproto.DestroyNotifyEvent: "event",
    xcb.xproto.UnmapNotifyEvent: "window",
    xcb.xproto.MapNotifyEvent: "window",
    xcb.xproto.ReparentNotifyEvent: "event",
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


class Window(Object, SingletonPool):
    """A basic X window."""

    __events = xcb.xproto.EventMask.NoEvent

    Visibility = xcb.xproto.Visibility
    Visibility.Unknown = -1

    class x(cachedproperty):
        """X coordinate."""
        def __get__(self):
            self._retrieve_geometry()

        def __set__(self, value):
            MainConnection().core.ConfigureWindow(self.xid,
                                                  xcb.xproto.ConfigWindow.X,
                                                  [ value ])

    class y(cachedproperty):
        """Y coordinate."""
        def __get__(self):
            self._retrieve_geometry()

        def __set__(self, value):
            MainConnection().core.ConfigureWindow(self.xid,
                                                  xcb.xproto.ConfigWindow.Y,
                                                  [ value ])

    class width(cachedproperty):
        """Width."""
        def __get__(self):
            self._retrieve_geometry()

        def __set__(self, value):
            MainConnection().core.ConfigureWindow(self.xid,
                                                  xcb.xproto.ConfigWindow.Width,
                                                  [ value ])

    class height(cachedproperty):
        """Height."""
        def __get__(self):
            self._retrieve_geometry()

        def __set__(self, value):
            MainConnection().core.ConfigureWindow(self.xid,
                                                  xcb.xproto.ConfigWindow.Height,
                                                  [ self.height ])

    class border_width(cachedproperty):
        """Border width."""
        def __get__(self):
            self._retrieve_geometry()

        def __set__(self, value):
            MainConnection().core.ConfigureWindow(self.xid,
                                                  xcb.xproto.ConfigWindow.BorderWidth,
                                                         [ value ])

    class visibility(rocachedproperty):
        """Visibility of the window.
        This can be either:
            * Window.Visibility.Unknown
            * Window.Visibility.Unobscured
            * Window.Visibility.PartiallyObscured
            * Window.Visibility.FullyObscured"""
        def __get__(self):
            return Window.Visibility.Unknown

    class border_color(cachedproperty):
        """Border color."""
        def __get__(self):
            raise AttributeError("Nobody knows how to fetch this.")

        def __set__(self, value):
            color = Color(self.get_root().default_colormap, value)
            MainConnection().core.ChangeWindowAttributes(self.xid,
                                                         xcb.xproto.CW.BorderPixel,
                                                         [ color.pixel ])
            return color

    class map_state(rocachedproperty):
        """Window mapping state."""
        def __get__(self):
            reply = MainConnection().core.GetWindowAttributes(self.xid).reply()
            return reply.map_state

    class _icccm_name(cachedproperty):
        """ICCCM window name."""
        def __get__(self):
            prop = MainConnection().core.GetProperty(False, self.xid,
                                                     Atom("WM_NAME").value,
                                                     xcb.xproto.GetPropertyType.Any,
                                                     0, 4096).reply()
            return byte_list_to_str(prop.value)

        def __set__(self, value):
            MainConnection().core.ChangeProperty(xcb.xproto.Property.NewValue,
                                                 self.xid,
                                                 Atom("WM_NAME").value,
                                                 Atom("STRING").value,
                                                 8, len(value), value)

    class _netwm_name(cachedproperty):
        """EWMH window name."""
        def __get__(self):
            prop = MainConnection().core.GetProperty(False, self.xid,
                                                     Atom("_NET_WM_NAME").value,
                                                     xcb.xproto.GetPropertyType.Any,
                                                     0, 4096).reply()
            return byte_list_to_str(prop.value)

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

    def __init__(self, xid):
        self.xid = xid
        # Mandatory, we except this.
        self._set_events(xcb.xproto.EventMask.StructureNotify
                         | xcb.xproto.EventMask.PropertyChange
                         | xcb.xproto.EventMask.VisibilityChange)
        # Receive events and errors from the X connection
        MainConnection().connect_signal(self._dispatch_events,
                                        signal=xcb.Event)
        MainConnection().connect_signal(self._dispatch_errors,
                                        signal=xcb.Error)

        super(Window, self).__init__()

    def get_root(self):
        # XXX lol...
        return MainConnection().roots[0]

    # I'm still not sure it belongs here, but well at least it's a good test
    def watch_children(self):
        """Maintain a list of children window."""
        # Avoid missing events
        with MainConnection():
            # Request children
            qt = MainConnection().core.QueryTree(self.xid)
            # Build children tree correctly
            self.on_reparent(self._on_reparent)
            self.on_create_subwindow(self._on_create_subwindow)
            self.on_destroy_subwindow(self._on_destroy_subwindow)
            reply = qt.reply()

        self.children = set()
        for w in reply.children:
            self.children.add(Window(w))

    def _is_event_for_me(self, event):
        """Guess if an X even is for us or not."""

        if event.__class__ in events_window_attribute.keys():
            return getattr(event, events_window_attribute[event.__class__]) == self.xid
        return False

    def _dispatch_events(self, signal, sender):
        """Dipatch signals that belongs to us."""
        if self._is_event_for_me(signal):
            self.emit_signal(signal)

    def _dispatch_errors(self, signal, sender):
        """Dispatch errors that belongs to us."""
        if signal.bad_value == self.xid:
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
        Window.x.set_cache(self, wg.x)
        Window.y.set_cache(self, wg.y)
        Window.width.set_cache(self, wg.width)
        Window.height.set_cache(self, wg.height)
        Window.border_width.set_cache(self, wg.border_width)

    @staticmethod
    def _on_configure_update_geometry(sender, signal):
        """Update window geometry from an event."""
        Window.x.set_cache(sender, signal.x)
        Window.y.set_cache(sender, signal.y)
        Window.width.set_cache(sender, signal.width)
        Window.height.set_cache(sender, signal.height)
        Window.border_width.set_cache(sender, signal.border_width)

    @staticmethod
    def _on_reparent(sender, signal):
        # Make sure we are not the one reparented
        if signal.window != sender.xid:
            if signal.parent == sender.xid:
                # We are adopting
                sender.children.add(Window(signal.window))
            else:
                sender.children.remove(Window(signal.window))

    _atom_to_property = {
        Atom("WM_NAME").value: "_icccm_name",
        Atom("_NET_WM_NAME").value: "_netwm_name",
    }

    @staticmethod
    def _on_property_change_del_cache(sender, signal):
        if sender._atom_to_property.has_key(signal.atom):
            # Erase cache
            delattr(sender, sender._atom_to_property[signal.atom])

    _property_renotify_map = {
        Notify("_icccm_name"): Notify("name"),
        Notify("_netwm_name"): Notify("name"),
    }

    @staticmethod
    def _property_renotify(sender, signal):
        """Reemit some notify events differently."""
        if sender._property_renotify_map.has_key(signal):
            sender.emit_signal(sender._property_renotify_map[signal])

    @staticmethod
    def _on_create_subwindow(sender, signal):
        """Add children when subwindows are created."""
        sender.children.add(Window(signal.window))

    @staticmethod
    def _on_destroy_subwindow(sender, signal):
        """Remove subwindow."""
        # Check it's not 'sender/self' that is being destroyed
        if signal.window != sender.xid:
            sender.children.remove(Window(signal.window))

    @staticmethod
    def _on_visibility_set_value(sender, signal):
        """Update visibility value."""
        Window.visibility.set_cache(sender, signal.state)

    # Methods
    def focus(self):
        """Give focus to a window.
        If focus is lost, it will go back to window's parent."""
        MainConnection().core.SetInputFocus(xcb.xproto.InputFocus.Parent,
                                            self.xid,
                                            xcb.xproto.Time.CurrentTime)

    def map(self):
        """Map a window on the screen."""
        MainConnection().core.MapWindow(self.xid)

    def unmap(self):
        """Unmap a window from the screen."""
        MainConnection().core.UnmapWindow(self.xid)

    def destroy(self):
        """Destroy a window."""
        MainConnection().core.DestroyWindow(self.xid)

    def grab_key(self, modifiers, keycode):
        """Grab a key on a window."""
        MainConnection().core.GrabKey(True,
                                      self.xid,
                                      modifiers,
                                      keycode,
                                      xcb.xproto.GrabMode.Async,
                                      xcb.xproto.GrabMode.Async)

    def ungrab_key(self, modifiers, keycode):
        """Ungrab a key on a window."""
        MainConnection().core.UngrabKey(keycode,
                                        self.xid,
                                        modifiers)

    def grab_button(self, modifiers, button):
        """Grab a button on a window."""
        MainConnection().core.GrabButton(False,
                                         self.xid,
                                         xcb.xproto.EventMask.ButtonPress
                                         | xcb.xproto.EventMask.ButtonRelease,
                                         # XXX Sync?
                                         xcb.xproto.GrabMode.Async,
                                         xcb.xproto.GrabMode.Async,
                                         xcb.xproto.NONE,
                                         xcb.xproto.NONE,
                                         button, modifiers)

    def ungrab_button(self, modifiers, button):
        """Ungrab a button on a window."""
        MainConnectino().core.UngrabButton(button,
                                           self.xid,
                                           modifiers)

    # Events handling
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
        """Connect a function to a subwindow destroy event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.DestroyNotifyEvent)
        return func

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

    def on_map_subwindow(self, func):
        """Connect a function to a subwindow map event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.MapNotifyEvent)
        return func

    def on_unmap_subwindow(self, func):
        """Connect a function to a subwindow unmap event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.UnmapNotifyEvent)
        return func

    def on_map_subwindow_request(self, func):
        """Connect a function to a subwindow mapping request event."""
        self._add_event(xcb.xproto.EventMask.SubstructureRedirectNotify)
        self.connect_signal(func, xcb.xproto.MapRequestEvent)
        return func

    def on_configure(self, func):
        """Connect a function to a configure notify event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.ConfigureNotifyEvent)
        return func

    def on_configure_subwindow(self, func):
        """Connect a function to a configure subwindow notify event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.ConfigureNotifyEvent)
        return func

    def on_configure_subwindow_request(self, func):
        """Connect a function to a configure request event."""
        self._add_event(xcb.xproto.EventMask.SubstructureRedirect)
        self.connect_signal(func, xcb.xproto.ConfigureRequestEvent)
        return func

    def on_reparent(self, func):
        """Connect a function to a reparent notify event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.ReparentNotifyEvent)
        return func

    def on_reparent_subwindow(self, func):
        """Connect a function to a subwindow reparent notify event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.ReparentNotifyEvent)
        return func

    def on_property_change(self, func):
        """Connect a function to a reparent notify event."""
        self._add_event(xcb.xproto.EventMask.PropertyChange)
        self.connect_signal(func, xcb.xproto.PropertyNotifyEvent)
        return func

    def on_reparent(self,func):
        """Connection a function to a reparent notify event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.ReparentNotifyEvent)
        return func

    def on_reparent_subwindow(self,func):
        """Connection a function to a reparent notify event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.ReparentNotifyEvent)
        return func

    def on_configure_subwindow_request(self, func):
        """Connection a function to a configure subwindow request event."""
        self._add_event(xcb.xproto.EventMask.SubstructureRedirect)
        self.connect_signal(func, xcb.xproto.ConfigureRequestEvent)
        return func

    def on_gravity(self, func):
        """Connection a function to a gravity event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.GravityNotifyEvent)
        return func

    def on_gravity_subwindow(self, func):
        """Connection a function to a gravity event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.GravityNotifyEvent)
        return func

    def on_circulate(self, func):
        """Connection a function to a circulate event."""
        self._add_event(xcb.xproto.EventMask.StructureNotify)
        self.connect_signal(func, xcb.xproto.CirculateNotifyEvent)
        return func

    def on_circulate_subwindow(self, func):
        """Connection a function to a circulate subwindow event."""
        self._add_event(xcb.xproto.EventMask.SubstructureNotify)
        self.connect_signal(func, xcb.xproto.CirculateNotifyEvent)
        return func

    def on_circulate_subwindow_request(self, func):
        """Connection a function to a circulate subwindow event."""
        self._add_event(xcb.xproto.EventMask.SubstructureRedirect)
        self.connect_signal(func, xcb.xproto.CirculateRequestEvent)
        return func

    def on_client_message(self, func):
        """Connect a function to a client message event."""
        self.connect_signal(func, xcb.xproto.ClientMessageEvent)
        return func

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__,
                           hex(self.xid))


# Handle ConfigureNotify to update cached attributes
Window.connect_class_signal(Window._on_configure_update_geometry,
                            xcb.xproto.ConfigureNotifyEvent)
# Handle PropertyNotify to update properties
Window.connect_class_signal(Window._on_property_change_del_cache,
                            xcb.xproto.PropertyNotifyEvent)
# Build visibility value
Window.connect_class_signal(Window._on_visibility_set_value,
                            xcb.xproto.VisibilityNotifyEvent)
# Reemit some Notify signals
Window.connect_class_signal(Window._property_renotify, Notify)


class CreatedWindow(Window):
    """Created window."""

    def __new__(cls, xid, *args, **kwargs):
        xid = MainConnection().generate_id()
        obj, do_init = super(CreatedWindow, cls).__new__(cls, xid)
        obj.xid = xid
        return obj, do_init

    def __init__(self, parent, x=0, y=0, width=1, height=1,
                 border_width=0, values={}):

        if parent is None or parent is self:
            raise ValueError("you have to set a parent to create your window")

        # Always listen to this events at creation.
        # Otherwise our cache might not be up to date.
        # XXX or grab while creating and calling super()
        self.__events = xcb.xproto.EventMask.StructureNotify \
                        | xcb.xproto.EventMask.PropertyChange \
                        | xcb.xproto.EventMask.VisibilityChange


        # XXX fix, no get_root
        create_window = \
        MainConnection().core.CreateWindowChecked(parent.get_root().root_depth,
                                                  self.xid,
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
        super(CreatedWindow, self).__init__(self.xid)

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
