"""Bazinga window objects."""

from base.property import cachedproperty, rocachedproperty
from base.object import Object, Notify
from base.singleton import SingletonPool
from x import MainConnection, byte_list_to_uint32, byte_list_to_str
from atom import Atom
from color import Color
from cursor import Cursor
import event

import xcb.xproto
from PIL import Image
import struct

events_window_attribute = {
    # Event: (event mask, attribute matching xid)
    xcb.xproto.KeyPressEvent: (xcb.xproto.EventMask.KeyPress, "event"),
    xcb.xproto.KeyReleaseEvent: (xcb.xproto.EventMask.KeyRelease, "event"),
    xcb.xproto.ButtonPressEvent: (xcb.xproto.EventMask.ButtonPress, "event"),
    xcb.xproto.ButtonReleaseEvent: (xcb.xproto.EventMask.ButtonRelease, "event"),
    xcb.xproto.MotionNotifyEvent: (xcb.xproto.EventMask.PointerMotion, "event"),
    xcb.xproto.EnterNotifyEvent: (xcb.xproto.EventMask.EnterWindow, "event"),
    xcb.xproto.LeaveNotifyEvent: (xcb.xproto.EventMask.LeaveWindow, "event"),
    xcb.xproto.FocusInEvent: (xcb.xproto.EventMask.FocusChange, "event"),
    xcb.xproto.FocusOutEvent: (xcb.xproto.EventMask.FocusChange, "event"),
    xcb.xproto.ExposeEvent: (xcb.xproto.EventMask.Exposure, "window"),
    xcb.xproto.VisibilityNotifyEvent: (xcb.xproto.EventMask.VisibilityChange, "window"),
    xcb.xproto.CreateNotifyEvent: (xcb.xproto.EventMask.SubstructureNotify, "parent"),
    xcb.xproto.DestroyNotifyEvent: (xcb.xproto.EventMask.SubstructureNotify, "event"),
    xcb.xproto.UnmapNotifyEvent: (xcb.xproto.EventMask.StructureNotify, "window"),
    xcb.xproto.MapNotifyEvent: (xcb.xproto.EventMask.StructureNotify, "window"),
    xcb.xproto.ReparentNotifyEvent: (xcb.xproto.EventMask.StructureNotify, "event"),
    xcb.xproto.ConfigureNotifyEvent: (xcb.xproto.EventMask.StructureNotify, "window"),
    xcb.xproto.ConfigureRequestEvent: (xcb.xproto.EventMask.SubstructureRedirect, "parent"),
    xcb.xproto.CirculateNotifyEvent: (xcb.xproto.EventMask.StructureNotify, "window"),
    xcb.xproto.CirculateRequestEvent: (xcb.xproto.EventMask.SubstructureRedirect, "window"),
    xcb.xproto.PropertyNotifyEvent: (xcb.xproto.EventMask.PropertyChange, "window"),
    xcb.xproto.ClientMessageEvent: (None, "window")
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

    class depth(rocachedproperty):
        """Window color depth."""
        def __get__(self):
            self._retrieve_geometry()

    class root(rocachedproperty):
        """Root window this window is attached on."""
        def __get__(self):
            self._retrieve_geometry()

    class above_sibling(cachedproperty):
        """Sibling which is under the window."""
        def __set__(self, window):
            MainConnection().core.ConfigureWindow(self.xid,
                                                  xcb.xproto.ConfigWindow.Sibling
                                                  | xcb.xproto.ConfigWindow.StackMode,
                                                  [ window.xid, xcb.xproto.StackMode.Above ])

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
            color = Color(self.colormap, value)
            MainConnection().core.ChangeWindowAttributes(self.xid,
                                                         xcb.xproto.CW.BorderPixel,
                                                         [ color.pixel ])
            return color

    class cursor(cachedproperty):
        """Window cursor."""
        def __get__(self):
            raise AttributeError("Nobody knows how to fetch this.")

        def __set__(self, value):
            value = Cursor(self.colormap, value)
            MainConnection().core.ChangeWindowAttributes(self.xid,
                                                         xcb.xproto.CW.Cursor,
                                                         [ value.xid ])
            return value

    class map_state(rocachedproperty):
        """Window mapping state."""
        def __get__(self):
            self._retrieve_window_attributes()

    class colormap(rocachedproperty):
        """Colormap of the window."""
        def __get__(self):
            self._retrieve_window_attributes()

    class visual(rocachedproperty):
        """Visual of the window."""
        def __get__(self):
            self._retrieve_window_attributes()

    class icon(cachedproperty):
        """Window icon."""
        def __get__(self):
            prop = MainConnection().core.GetProperty(False, self.xid,
                                                     Atom("_NET_WM_ICON").value,
                                                     Atom("CARDINAL").value,
                                                     # Max icon size is:
                                                     #  w  *  h  * (rgba)
                                                     0, 256*256*4).reply()
            if len(prop.value) % 4 == 0:
                width, height = byte_list_to_uint32(prop.value[:8])
                return Image.frombuffer("RGBA",
                                        (width, height),
                                        byte_list_to_str(prop.value[8:]),
                                        "raw", "ARGB", 0, 1)

        def __set__(self, image):
            _imagedata = image.tostring("raw", "RGBA", 0, 1)
            # Convert to ARGB
            imagedata = ""
            for i in range(0, len(_imagedata), 4):
                imagedata += _imagedata[i + 3] # A
                imagedata += _imagedata[i]     # R
                imagedata += _imagedata[i + 1] # G
                imagedata += _imagedata[i + 2] # B

            data = struct.pack("II{0}s".format(len(imagedata)),
                               image.size[0], image.size[1], imagedata)
            MainConnection().core.ChangeProperty(xcb.xproto.Property.NewValue,
                                                 self.xid,
                                                 Atom("_NET_WM_ICON").value,
                                                 Atom("CARDINAL").value,
                                                 32, len(data) / 4, data)

    class transient_for(rocachedproperty):
        """Window this window is transient for."""
        def __get__(self):
            prop = MainConnection().core.GetProperty(False, self.xid,
                                                     Atom("WM_TRANSIENT_FOR").value,
                                                     Atom("WINDOW").value,
                                                     0, 1).reply()
            if prop.value:
                return Window(byte_list_to_uint32(prop.value)[0])

        def __set__(self, value):
            MainConnection().core.ChangeProperty(xcb.xproto.Property.NewValue,
                                                 self.xid,
                                                 Atom("WM_TRANSIENT_FOR").value,
                                                 Atom("WINDOW").value,
                                                 32, 1, value.xid)

    class machine(rocachedproperty):
        """Machine this window is running on."""
        def __get__(self):
            return MainConnection().get_text_property(self, "WM_CLIENT_MACHINE")

        def __set__(self, value):
            MainConnection().set_text_property(self, "WM_CLIENT_MACHINE", value)

    class _icccm_name(cachedproperty):
        """ICCCM window name."""
        def __get__(self):
            return MainConnection().get_text_property(self, "WM_NAME")

        def __set__(self, value):
            MainConnection().set_text_property(self, "WM_NAME", value)

    class _netwm_name(cachedproperty):
        """EWMH window name."""
        def __get__(self):
            return MainConnection().get_text_property(self, "_NET_WM_NAME")

        def __set__(self, value):
            MainConnection().set_text_property(self, "_NET_WM_NAME", value)

    @property
    def name(self):
        """Window name."""
        return self._netwm_name or self._icccm_name

    @name.setter
    def name(self, value):
        self._icccm_name = self._netwm_name = value

    class _icccm_icon_name(cachedproperty):
        """ICCCM window name."""
        def __get__(self):
            return MainConnection().get_text_property(self, "WM_ICON_NAME")

        def __set__(self, value):
            MainConnection().set_text_property(self, "WM_ICON_NAME", value)

    class _netwm_icon_name(cachedproperty):
        """EWMH window icon name."""
        def __get__(self):
            return MainConnection().get_text_property(self, "_NET_WM_ICON_NAME")

        def __set__(self, value):
            MainConnection().set_text_property(self, "_NET_WM_ICON_NAME", value)

    @property
    def icon_name(self):
        """Window icon name."""
        return self._netwm_icon_name or self._icccm_icon_name

    @name.setter
    def icon_name(self, value):
        self._icccm_icon_name = self._netwm_icon_name = value

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

    # I'm still not sure it belongs here, but well at least it's a good test
    def watch_children(self):
        """Maintain a list of children window."""
        # Avoid missing events
        with MainConnection():
            # Request children
            qt = MainConnection().core.QueryTree(self.xid)
            # Build children tree correctly
            # XXX fixme, this is now on_event()
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
            return getattr(event, events_window_attribute[event.__class__][1]) == self.xid
        return False

    def _dispatch_events(self, signal):
        """Dipatch signals that belongs to us."""
        if self._is_event_for_me(signal):
            self.emit_signal(signal)

    def _dispatch_errors(self, signal):
        """Dispatch errors that belongs to us."""
        if signal.bad_value == self.xid:
            self.emit_signal(signal)

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
        Window.depth.set_cache(self, wg.depth)
        Window.root.set_cache(self, Window(wg.root))

    def _retrieve_window_attributes(self):
        """Update windows attributes."""
        wa = MainConnection().core.GetWindowAttributes(self.xid).reply()
        Window.map_state.set_cache(self, wa.map_state)
        Window.colormap.set_cache(self, wa.colormap)
        Window.visual.set_cache(self, wa.visual)

    @staticmethod
    def _on_configure_update_geometry(sender, signal):
        """Update window geometry from an event."""
        Window.x.set_cache(sender, signal.x)
        Window.y.set_cache(sender, signal.y)
        Window.width.set_cache(sender, signal.width)
        Window.height.set_cache(sender, signal.height)
        Window.border_width.set_cache(sender, signal.border_width)
        Window.above_sibling.set_cache(sender, signal.above_sibling)

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
        Atom("WM_ICON_NAME").value: "_icccm_icon_name",
        Atom("_NET_WM_ICON_NAME").value: "_netwm_icon_name",
        Atom("WM_TRANSIENT_FOR").value: "transient_for",
        Atom("WM_CLIENT_MACHINE").value: "machine",
        Atom("_NET_WM_ICON").value: "icon",
    }

    @staticmethod
    def _on_property_change_del_cache(sender, signal):
        if sender._atom_to_property.has_key(signal.atom):
            # Erase cache
            delattr(sender, sender._atom_to_property[signal.atom])

    _property_renotify_map = {
        Notify("_icccm_name"): Notify("name"),
        Notify("_netwm_name"): Notify("name"),
        Notify("_icccm_icon_name"): Notify("icon_name"),
        Notify("_netwm_icon_name"): Notify("icon_name"),
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

    @staticmethod
    def _build_key_button_event(xevent, cls):
        event = cls(xevent.state, xevent.detail)
        event.x = xevent.event_x
        event.y = xevent.event_y
        event.root_x = xevent.root_x
        event.root_y = xevent.root_y
        return event

    @staticmethod
    def _on_key_press_emit_event(sender, signal):
        sender.emit_signal(_build_key_button_event(signal, event.KeyPress))

    @staticmethod
    def _on_key_release_emit_event(sender, signal):
        sender.emit_signal(_build_key_button_event(signal, event.KeyRelease))

    @staticmethod
    def _on_button_press_emit_event(sender, signal):
        sender.emit_signal(_build_key_button_event(signal, event.ButtonPress))

    @staticmethod
    def _on_button_release_emit_event(sender, signal):
        sender.emit_signal(_build_key_button_event(signal, event.ButtonRelease))

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
    def _on_event(self, event):
        if events_window_attribute[event][0]:
            self._add_event(events_window_attribute[event][0])
        def _on_event(func):
            self.connect_signal(func, event)
            return func
        return _on_event

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
# Handle key/button press/release
Window.connect_class_signal(Window._on_key_press_emit_event, xcb.xproto.KeyPressEvent)
Window.connect_class_signal(Window._on_key_release_emit_event, xcb.xproto.KeyReleaseEvent)
Window.connect_class_signal(Window._on_button_press_emit_event, xcb.xproto.ButtonPressEvent)
Window.connect_class_signal(Window._on_button_release_emit_event, xcb.xproto.ButtonReleaseEvent)
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


        create_window = \
        MainConnection().core.CreateWindowChecked(xcb.xproto.WindowClass.CopyFromParent,
                                                  self.xid,
                                                  parent.xid,
                                                  x, y, width, height,
                                                  border_width,
                                                  xcb.xproto.WindowClass.CopyFromParent,
                                                  xcb.xproto.WindowClass.CopyFromParent,
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
