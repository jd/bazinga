import pyev
import xcb

from screen import Screen, Output
from base.singleton import Singleton
from base.object import Object
from base.property import Property
from loop import MainLoop

def byte_list_to_str(blist):
    """Convert a byte list to a string."""

    return "".join(map(chr, blist))


class Connection(Object, xcb.Connection):
    """A X connection."""

    def __init__(self, loop=MainLoop(), *args, **kw):
        """Initialize a X connection."""

        import xcb.xproto
        import xcb.randr
        import xcb.xinerama

        xcb.Connection.__init__(self, *args, **kw)

        try:
            self.randr = self(xcb.randr.key)
        except xcb.ExtensionException:
            randr_queryversion_c = None
        else:
            # Check that RandR extension is at least 1.1
            randr_queryversion_c = self.randr.QueryVersion(1, 1)

        try:
            self.xinerama = self(xcb.xinerama.key)
        except xcb.ExtensionException:
            xinerama_isactive_c = None
        else:
            # Check that Xinerama is active
            xinerama_isactive_c = self.xinerama.IsActive()

        self.roots = []
        from window import Window
        for root in self.get_setup().roots:
            self.roots.append(Window(xid = root.root,
                                     connection = self,
                                     x = 0,
                                     y = 0,
                                     width = root.width_in_pixels,
                                     height = root.height_in_pixels,
                                     root_depth = root.root_depth,
                                     root_visual = root.root_visual,
                                     default_colormap = root.default_colormap))

        self.screens = []

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
                        screen = Screen(x = crtc_info.x,
                                        y = crtc_info.y,
                                        width = crtc_info.width,
                                        height = crtc_info.height,
                                        root = root,
                                        outputs = [])
                        self.screens.append(screen)

                        # Prepare output info requests
                        output_info_c = Connection.prepare_requests(self.randr.GetOutputInfo,
                                crtc_info.outputs, 0, xcb.xproto.Time.CurrentTime)

                        for output_info_cookie in output_info_c:
                            output_info = output_info_cookie.reply()
                            screen.outputs.append(Output(name = byte_list_to_str(output_info.name),
                                                         mm_width = output_info.mm_width,
                                                         mm_height = output_info.mm_height))

        elif xinerama_isactive_c and xinerama_isactive_c.reply().state:
            screens_info = self.xinerama.QueryScreens().reply()
            for screen_info in screens_info.screen_info:
                self.screens.append(Screen(x = screen_info.x_org,
                                           y = screen_info.y_org,
                                           width = screen_info.width,
                                           # There is only one root if we have Xinerama
                                           root = self.roots[0],
                                           height = screen_info.height))

        else:
            for root, xroot in zip(self.roots, self.get_setup().roots):
                self.screens.append(Screen(x = 0, y = 0,
                                           width = root.width_in_pixels,
                                           height = root.height_in_pixels,
                                           root = root,
                                           outputs = [ Output(mm_width = xroot.width_in_millimeters,
                                                              mm_height = xroot.height_in_millimeters) ]))

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

    def _set_events(self, events):
        """Set events that shall be received by the X connection."""

        for root in self.roots:
            root.set_events(events)


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
        self.emit_signal(self.poll_for_event())

    def _prepare(self, watcher, events):
        self.flush()


class MainConnection(Singleton, Connection):
    """Main X connection of bazinga."""

    pass


class XObject(Object):
    """A generic X object."""

    connection = Property("Connection to the X server.", writable=False, type=Connection)

    def __init__(self, connection=None, **kw):
        if connection is None:
            connection = MainConnection()
        self.connection = connection
        Object.__init__(self, **kw)
