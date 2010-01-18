import pyev
import xcb

from screen import Screen, Output
from basic import Singleton, Object, Property
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
                                     root_visual = root.root_visual))

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

        pyev.Io(self.get_file_descriptor(), pyev.EV_READ, loop, Connection.on_io)


    def set_events(self, events):

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


    @staticmethod
    def on_io(watcher, events):
        event = watcher.poll_for_event()


class MainConnection(Singleton, Connection):

    """Main X connection of bazinga."""

    pass


class XObject(Object):

    """A generic X object."""

    connection = Property(writable=False, type=Connection)


    def __init__(self, connection=None, **kw):

        if connection is None:
            connection = MainConnection()

        XObject.connection.init(self, connection)

        Object.__init__(self, **kw)
