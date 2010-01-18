import xcb.xproto

from x import XObject
from basic import Property

class Color(XObject):

    """A color."""


    def __init__(self, colormap, name=None, red=0, blue=0, green=0, alpha=0, **kw):

        XObject.__init__(self, **kw)

        if name is None or name[0] == '#':
            if name is not None:
                len_name = len(name)
                if len_name != 7 or len_name != 9:
                    raise ValueError("Bad color name {0}.".format(name))

                red = int(name[1:3], 16) * 257
                green = int(name[3:5], 16) * 257
                blue = int(name[5:7], 16) * 257

                if len_name == 9:
                    alpha = int(name[7:9], 16) * 257

            for value in [ red, blue, green, alpha ]:
                if value < 0 or value >= 65535:
                    raise ValueError("Color attribute value is too high.")

            self.cookie = self.connection.core.AllocColor(colormap, red, green, blue)
        else:
            if alpha < 0 or alpha >= 65535:
                raise ValueError("Color attribute value is too high.")
            self.cookie = self.connection.core.AllocNamedColor(colormap, len(name), name)
            self._name = name

        self.alpha = alpha


    def read_reply(self):

        if hasattr(self, "cookie"):
            reply = self.cookie.reply()
            del self.cookie
            self._pixel = reply.pixel
            if isinstance(reply, xcb.xproto.AllocNamedColorReply):
                self._red = reply.exact_red
                self._blue = reply.exact_blue
                self._green = reply.exact_green
            else:
                self._red = reply.red
                self._green = reply.green
                self._blue = reply.blue


    @property
    def hex(self):

        self.read_reply()
        return "#{0:<02x}{1:<02x}{2:<02x}{3:<02x}".format(self.red / 257,
                                                          self.green / 257,
                                                          self.blue / 257,
                                                          self.alpha / 257)


    @property
    def name(self):

        if hasattr(self, "_name"):
            return self._name
        return self.hex


    @property
    def pixel(self):

        self.read_reply()
        return self._pixel


    @property
    def red(self):

        self.read_reply()
        return self._red


    @property
    def green(self):

        self.read_reply()
        return self._green

    @property
    def blue(self):

        self.read_reply()
        return self._blue
