import pyev

import xcb.xproto
import xcb.randr

from bazinga.window import Window
from bazinga.screen import Screen, Output
from bazinga.core.mainloop import MainLoop
from bazinga.basic import Singleton


def byte_list_to_str(blist):
    ret = ""
    for char in blist:
        ret += chr(char)
    return ret

class Connection(Singleton, pyev.Io):

    def __init__(self, *args, **kw):
        if not hasattr(self, "connection"):
            self.connection = xcb.connect(*args, **kw)
            self.connection.randr = self.connection(xcb.randr.key)

            # Check that RandR extension is at least 1.1
            randr_queryversion_c = self.connection.randr.QueryVersion(1, 1)

            self.roots = []
            self.screens = []
            for root in self.connection.get_setup().roots:
                self.roots.append(Window(id=root.root))

            have_randr = randr_queryversion_c.reply();

            # Does it have RandR ?
            if have_randr:
                screen_resources_c = Connection.prepare_requests(self.connection.randr.GetScreenResources,
                        list(root.id for root in self.roots), 0)
                for screen_resources_cookie in screen_resources_c:
                    screen_resources = screen_resources_cookie.reply()

                    crtc_info_c = Connection.prepare_requests(self.connection.randr.GetCrtcInfo,
                            screen_resources.crtcs, 0, xcb.xproto.Time.CurrentTime)

                    for crtc_info_cookie in crtc_info_c:
                        crtc_info = crtc_info_cookie.reply()
                        # Does the CRTC have outputs?
                        if len(crtc_info.outputs):
                            screen = Screen(x=crtc_info.x,
                                    y=crtc_info.y,
                                    width=crtc_info.width,
                                    height=crtc_info.height,
                                    outputs=[])
                            self.screens.append(screen)

                            # Prepare output info requests
                            output_info_c = Connection.prepare_requests(self.connection.randr.GetOutputInfo,
                                    crtc_info.outputs, 0, xcb.xproto.Time.CurrentTime)

                            for output_info_cookie in output_info_c:
                                output_info = output_info_cookie.reply()
                                screen.outputs.append(Output(name=byte_list_to_str(output_info.name),
                                        mm_width=output_info.mm_width,
                                        mm_height=output_info.mm_height))

            elif have_xinerama:
                pass
            else:
                pass
                
            pyev.Io.__init__(self, self.connection.get_file_descriptor(),
                    pyev.EV_READ, MainLoop(), Connection.on_io)

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
        event = watcher.connection.poll_for_event()
        print event
