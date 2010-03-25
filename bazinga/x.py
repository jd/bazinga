import pyev
import xcb.xproto
import traceback
import struct
import weakref

from screen import Screen, ScreenXinerama, ScreenRandr, Output, OutputRandr
from base.singleton import Singleton, SingletonPool
from base.property import rocachedproperty
from base.object import Object
from loop import MainLoop
from atom import Atom


def byte_list_to_str(blist):
    """Convert a byte list to a string."""
    return struct.unpack_from("{0}s".format(len(blist)), blist.buf())[0]


def byte_list_to_uint32(blist):
    """Convert a byte list to a integer."""
    return struct.unpack_from("{0}I".format(len(blist) / 4), blist.buf())


class Connection(Object, xcb.Connection):
    """A X connection."""

    def __init__(self, loop=MainLoop(), *args, **kw):
        """Initialize a X connection."""

        super(Connection, self).__init__(*args, **kw)

        # Initialize IO watcher
        self._io = pyev.Io(self.get_file_descriptor(),
                           pyev.EV_READ, loop,
                           self._on_io)
        self._io.start()

        # Initialize Prepare watcher
        self._prepare = pyev.Prepare(loop, self._prepare)
        self._prepare.start()

        # Store loop
        self.loop = loop

    class roots(rocachedproperty):
        """Root windows."""
        def __get__(self):
            roots = []
            from window import Window
            for root in self.get_setup().roots:
                root_window = Window(self, root.root)
                Window.x.set_cache(root_window, 0)
                Window.y.set_cache(root_window, 0)
                Window.width.set_cache(root_window, root.width_in_pixels)
                Window.height.set_cache(root_window, root.height_in_pixels)
                roots.append(root_window)

            return roots

    class screens(rocachedproperty):
        """Screens connection."""
        def __get__(self):
            try:
                import xcb.randr
                self.randr = self(xcb.randr.key)
            except:
                randr_queryversion_c = None
            else:
                # Check that RandR extension is at least 1.1
                randr_queryversion_c = self.randr.QueryVersion(1, 1)

            try:
                import xcb.xinerama
                self.xinerama = self(xcb.xinerama.key)
            except:
                xinerama_isactive_c = None
            else:
                # Check that Xinerama is active
                xinerama_isactive_c = self.xinerama.IsActive()

            screens = []

            # Does it have RandR ?
            if randr_queryversion_c and randr_queryversion_c.reply():
                screen_resources_c = zip(self.roots,
                                         self.prepare_requests(self.randr.GetScreenResources,
                                                               self.roots, 0))
                for root, screen_resources_cookie in screen_resources_c:
                    screen_resources = screen_resources_cookie.reply()
                    screens.extend([ ScreenRandr(self, xid, root) for xid in
                                   screen_resources.crtcs ])
            elif xinerama_isactive_c and xinerama_isactive_c.reply().state:
                screens_info = self.xinerama.QueryScreens().reply()
                xid = 0
                for screen_info in screens_info.screen_info:
                    # There is only one root if we have Xinerama
                    screen = ScreenXinerama(self, xid, self.roots[0])
                    ScreenXinerama.x.set_cache(screen, screen_info.x_org)
                    ScreenXinerama.y.set_cache(screen, screen_info.y_org)
                    ScreenXinerama.width.set_cache(screen, screen_info.width)
                    ScreenXinerama.height.set_cache(screen, screen_info.height)
                    screens.append(screen)
                    xid += 1
            else:
                for i in xrange(len(self.roots)):
                    screens.append(Screen(self, i, self.roots[i]))

            return screens

    def __enter__(self):
        self.core.GrabServer()
        return self

    def __exit__(self, type, value, traceback):
        self.core.UngrabServer()

    @staticmethod
    def prepare_requests(method, variable_list, position, *args):
        """Prepare a bunch of requests."""
        cookies = []
        for var in variable_list:
            arguments = list(args)
            arguments.insert(position, var)
            cookies.append(method(*arguments))
        return cookies

    def _on_io(self, watcher, events):
        try:
            while True:
                try:
                    event = self.poll_for_event()
                except xcb.ProtocolException as error:
                    self.emit_signal(error.args[0])
                else:
                    if event:
                        self.emit_signal(event)
                    else:
                        # No more event
                        break
        except Exception:
            traceback.print_exc()

    def _prepare(self, watcher, events):
        self.flush()

    def set_text_property(self, window, atom_name, value):
        if isinstance(value, unicode):
            string_atom = Atom(self, "UTF8_STRING")
            value = value.encode("UTF-8")
        else:
            string_atom = Atom(self, "STRING")
        self.core.ChangeProperty(xcb.xproto.Property.NewValue,
                                 window,
                                 Atom(self, atom_name).value,
                                 string_atom,
                                 8, len(value), value)

    def get_text_property(self, window, atom_name):
        prop = self.core.GetProperty(False, window,
                                     Atom(self, atom_name).value,
                                     xcb.xproto.GetPropertyType.Any,
                                     0, 4096).reply()
        if prop.type == Atom(self, "UTF8_STRING").value:
            return unicode(byte_list_to_str(prop.value), "UTF-8")
        elif prop.type == Atom(self, "STRING").value:
            return byte_list_to_str(prop.value)

    def grab_pointer(self, window, cursor="left_ptr", confine_to=None):
        """Grab pointer on a window."""
        from cursor import Cursor
        confine_to = confine_to or window
        self.core.GrabPointer(False, window,
                              xcb.xproto.EventMask.ButtonPress
                              | xcb.xproto.EventMask.ButtonRelease
                              | xcb.xproto.EventMask.PointerMotion,
                              xcb.xproto.GrabMode.Async,
                              xcb.xproto.GrabMode.Async,
                              confine_to,
                              Cursor(window.colormap, cursor),
                              xcb.xproto.Time.CurrentTime)

    def ungrab_pointer(self):
        self.core.UngrabPointer(xcb.xproto.Time.CurrentTime)


class MainConnection(Singleton, Connection):
    """Main X connection of bazinga."""
    pass

class XObject(SingletonPool, Object, int):

    # All X objects are here, indexed by xid
    _SingletonPool__instances = weakref.WeakValueDictionary()

    @staticmethod
    def __getpoolkey__(connection, xid):
        return (id(connection), xid)

    def __new__(cls, connection, xid):
        return super(XObject, cls).__new__(cls, xid)

    def __init__(self, connection, xid):
        self.connection = connection

    @classmethod
    def create(cls, connection):
        return cls(connection, connection.generate_id())

    # Use default format from object rather than from int
    __str__ = object.__str__

    def __repr__(self):
        return "<{0} 0x{1:x} at 0x{2:x}>".format(self.__class__.__name__,
                                                 int(self), id(self))
