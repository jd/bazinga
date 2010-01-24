import xcb.xproto

from x import MainConnection
from base.object import Object
from base.memoize import memoize

class _Color(Object):
    """Generic color class."""

    def read_reply(self):
        if hasattr(self, "cookie"):
            reply = self.cookie.reply()
            del self.cookie
            self._pixel = reply.pixel
            return reply

    @property
    def hex(self):
        self.read_reply()
        return "#{0:<02x}{1:<02x}{2:<02x}{3:<02x}".format(self.red / 257,
                                                          self.green / 257,
                                                          self.blue / 257,
                                                          self.alpha / 257)

    @property
    def name(self):
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

    @property
    def alpha(self):
        return self._alpha

    def __str__(self):
        return self.name


class NamedColor(_Color):
    """A named color."""

    def __init__(self, colormap, name, alpha=65535):
        if alpha < 0 or alpha > 65535:
            raise ValueError("Bad alpha value.")

        self.cookie = MainConnection().core.AllocNamedColor(colormap, len(name), name)
        self._name = name
        self._alpha = alpha

        super(NamedColor, self).__init__()

    def read_reply(self):
        reply = _Color.read_reply(self)
        if reply:
            self._red = reply.exact_red
            self._green = reply.exact_green
            self._blue = reply.exact_blue
            return reply

    @property
    def name(self):
        return self._name

class ValueColor(_Color):
    """A color by value."""

    def __init__(self, colormap, red=0, green=0, blue=0, alpha=65535):

        for value in [ red, blue, green, alpha ]:
            if value < 0 or value > 65535:
                raise ValueError("Color attribute value is too high.")

        self.cookie = MainConnection().core.AllocColor(colormap, red, green, blue)
        self._alpha = alpha

        super(ValueColor, self).__init__()

    def read_reply(self):
        reply = _Color.read_reply(self)
        if reply:
            self._red = reply.red
            self._green = reply.green
            self._blue = reply.blue
            return reply


class HexColor(ValueColor):
    """An hexadecimal color."""

    def __init__(self, colormap, name, alpha=65535, **kw):
        len_name = len(name)

        if len_name != 6 and len_name != 8:
            raise ValueError("Bad color name {0}.".format(name))

        red = int(name[1:3], 16) * 257
        green = int(name[3:5], 16) * 257
        blue = int(name[5:7], 16) * 257

        if len_name == 9:
            alpha = int(name[7:9], 16) * 257

        super(HexColor, self).__init__(colormap, red, green, blue, alpha, **kw)


@memoize
def Color(colormap, color=None, red=0, green=0, blue=0, alpha=65535):
    """Create a color. You should specify name, or RGB value."""

    if color:
        # Already color type :-)
        if isinstance(color, _Color):
            return color
        else:
            if color[0] == '#':
                return HexColor(colormap, color[1:], alpha)
            else:
                return NamedColor(colormap, color, alpha)
    else:
        return ValueColor(colormap, red, green, blue, alpha)
