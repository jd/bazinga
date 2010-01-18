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
                    self.alpha = int(name[7:9], 16) * 257
                else:
                    self.alpha = 0

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
            self.reply = self.cookie.reply()
            del self.cookie
            if self._name is None:

    @property
    def hex(self):
        return "{0}{1}{2}{3}".format(hex(red / 257)[2:],
                                     hex(green / 257)[2:],
                                     hex(blue / 257)[2:],
                                     hex(alpha / 257)[2:])


    @property
    def name(self):

        if hasattr(self, "_name"):
            return self._name
        return self.hex


    @property
    def pixel(self):

        self.read_reply()
        return self.reply.pixel


    @property
    def red(self):

        self.read_reply()
        return self.reply.red


    @property
    def green(self):

        self.read_reply()
        return self.reply.green

    @property
    def blue(self):

        self.read_reply()
        return self.reply.blue
