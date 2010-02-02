import pyev
import xcb.xproto
import traceback

from screen import Screen, Output
from base.singleton import Singleton
from base.property import cachedproperty
from base.object import Object
from loop import MainLoop
from atom import Atom

def byte_list_to_str(blist):
    """Convert a byte list to a string."""
    return "".join(map(chr, blist))


def byte_list_to_unicode(blist):
    """Convert a byte list to a unicode string."""
    return u"".join(map(unichr, blist))


def byte_list_to_int(blist):
    """Convert a byte list to a integer."""
    if len(blist) > 0:
        value = 0
        for i in range(len(blist)):
            value |= blist[i] << i * 8
        return value


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

    class roots(cachedproperty):
        """Root windows."""
        def __get__(self):
            roots = []
            from window import Window
            for root in self.get_setup().roots:
                root_window = Window(xid=root.root)
                Window.x.set_cache(root_window, 0)
                Window.y.set_cache(root_window, 0)
                Window.width.set_cache(root_window, root.width_in_pixels)
                Window.height.set_cache(root_window, root.height_in_pixels)
                # Extra attributes
                root_window.default_colormap = root.default_colormap
                root_window.root_depth = root.root_depth
                root_window.root_visual = root.root_visual
                roots.append(root_window)

            return roots

    class screens(cachedproperty):
        """Screens connection."""
        def __get__(self):
            screens = []

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

            # Does it have RandR ?
            if randr_queryversion_c and randr_queryversion_c.reply():
                screen_resources_c = zip(self.roots, Connection.prepare_requests(self.randr.GetScreenResources,
                                                                                 list(root.xid for root in self.roots), 0))
                for root, screen_resources_cookie in screen_resources_c:
                    screen_resources = screen_resources_cookie.reply()

                    crtc_info_c = Connection.prepare_requests(self.randr.GetCrtcInfo,
                                                              screen_resources.crtcs, 0,
                                                              xcb.xproto.Time.CurrentTime)

                    for crtc_info_cookie in crtc_info_c:
                        crtc_info = crtc_info_cookie.reply()
                        # Does the CRTC have outputs?
                        if len(crtc_info.outputs):
                            screen = Screen()
                            screen.x = crtc_info.x
                            screen.y = crtc_info.y
                            screen.width = crtc_info.width
                            screen.height = crtc_info.height
                            screen.root = root
                            screen.outputs = []
                            screens.append(screen)

                            # Prepare output info requests
                            output_info_c = Connection.prepare_requests(self.randr.GetOutputInfo,
                                    crtc_info.outputs, 0, xcb.xproto.Time.CurrentTime)

                            for output_info_cookie in output_info_c:
                                output_info = output_info_cookie.reply()
                                output = Output()
                                output.name = byte_list_to_str(output_info.name)
                                output.mm_width = output_info.mm_width
                                output.mm_height = output_info.mm_height
                                screen.outputs.append(output)

            elif xinerama_isactive_c and xinerama_isactive_c.reply().state:
                screens_info = self.xinerama.QueryScreens().reply()
                for screen_info in screens_info.screen_info:
                    screen = Screen()
                    screen.x = screen_info.x_org
                    screen.y = screen_info.y_org
                    screen.width = screen_info.width
                    screen.height = screen_info.height
                    # There is only one root if we have Xinerama
                    root = self.roots[0]
                    screens.append(screen)
            else:
                for root, xroot in zip(self.roots, self.get_setup().roots):
                    screen = Screen()
                    screen.x = screen.y = 0
                    screen.width = root.width_in_pixels
                    screen.height = root.height_in_pixels
                    screen.root = root
                    output = Output()
                    output.mm_width = xroot.width_in_millimeters
                    output.mm_height = xroot.height_in_millimeters
                    screen.outputs = [ output ]
                    screens.append(screen)

            return screens

    def sync(self):
        """Synchronize connection."""
        self.core.GetInputFocus().reply()

    def grab(self):
        self.core.GrabServer()
        self.sync()

    def ungrab(self):
        self.core.UngrabServer()

    def __enter__(self):
        self.grab()
        return self

    def __exit__(self, type, value, traceback):
        self.ungrab()

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
            string_atom = Atom("UTF8_STRING")
            value = value.encode("UTF-8")
        else:
            string_atom = Atom("STRING")
        self.core.ChangeProperty(xcb.xproto.Property.NewValue,
                                 window.xid,
                                 Atom(atom_name).value,
                                 string_atom,
                                 8, len(value), value)

    def get_text_property(self, window, atom_name):
        prop = MainConnection().core.GetProperty(False, window.xid,
                                                 Atom(atom_name).value,
                                                 xcb.xproto.GetPropertyType.Any,
                                                 0, 4096).reply()
        if prop.type == Atom("UTF8_STRING").value:
            return byte_list_to_unicode(prop.value)
        elif prop.type == Atom("STRING").value:
            return byte_list_to_str(prop.value)


class MainConnection(Singleton, Connection):
    """Main X connection of bazinga."""
    pass
