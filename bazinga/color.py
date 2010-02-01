import xcb.xproto

from x import MainConnection
from base.object import Object
from base.memoize import memoize
from base.property import rocachedproperty

class XColor(Object):
    """Generic color class."""

    class pixel(rocachedproperty):
        """Pixel value of the color."""
        def __get__(self):
            self._read_reply()

    class red(rocachedproperty):
        """Red value of the color."""
        def __get__(self):
            self._read_reply()

    class green(rocachedproperty):
        """Green value of the color."""
        def __get__(self):
            self._read_reply()

    class blue(rocachedproperty):
        """Blue value of the color."""
        def __get__(self):
            self._read_reply()

    class alpha(rocachedproperty):
        """Alpha value of the color."""
        def __get__(self):
            self._read_reply()

    class hex(rocachedproperty):
        """Hexadecimal representation of the color."""
        def __get__(self):
            return "#{0:<02x}{1:<02x}{2:<02x}{3:<02x}".format(self.red / 257,
                                                              self.green / 257,
                                                              self.blue / 257,
                                                              self.alpha / 257)

    def _read_reply(self):
        if hasattr(self, "_cookie"):
            reply = self._cookie.reply()
            del self._cookie
            XColor.pixel.set_cache(self, reply.pixel)
            return reply


    @property
    def name(self):
        """Name of the color."""
        return self.hex

    def __str__(self):
        return self.name


class NamedColor(XColor):
    """A named color."""

    class name(rocachedproperty):
        __doc__  = XColor.name.__doc__

    def __init__(self, colormap, name, alpha=65535):
        if alpha < 0 or alpha > 65535:
            raise ValueError("Bad alpha value.")

        self._cookie = MainConnection().core.AllocNamedColor(colormap, len(name), name)
        NamedColor.name.set_cache(self, name)
        NamedColor.alpha.set_cache(self, alpha)

        super(NamedColor, self).__init__()

    def _read_reply(self):
        reply = XColor._read_reply(self)
        if reply:
            NamedColor.red.set_cache(self, reply.exact_red)
            NamedColor.green.set_cache(self, reply.exact_green)
            NamedColor.blue.set_cache(self, reply.exact_blue)
            return reply


class ValueColor(XColor):
    """A color by value."""

    def __init__(self, colormap, red=0, green=0, blue=0, alpha=65535):

        for value in [ red, blue, green, alpha ]:
            if value < 0 or value > 65535:
                raise ValueError("Color attribute value is too high.")

        self._cookie = MainConnection().core.AllocColor(colormap, red, green, blue)
        ValueColor.alpha.set_cache(self, alpha)

        super(ValueColor, self).__init__()

    def _read_reply(self):
        reply = XColor._read_reply(self)
        if reply:
            ValueColor.red.set_cache(self, reply.red)
            ValueColor.green.set_cache(self, reply.green)
            ValueColor.blue.set_cache(self, reply.blue)
            return reply


class HexColor(ValueColor):
    """An hexadecimal color."""

    def __init__(self, colormap, name, alpha=65535):
        len_name = len(name)

        if len_name != 6 and len_name != 8:
            raise ValueError("Bad color name {0}.".format(name))

        red = int(name[1:3], 16) * 257
        green = int(name[3:5], 16) * 257
        blue = int(name[5:7], 16) * 257

        if len_name == 9:
            alpha = int(name[7:9], 16) * 257

        super(HexColor, self).__init__(colormap, red, green, blue, alpha)


@memoize(ignore_first=False)
def Color(colormap, color=None, red=0, green=0, blue=0, alpha=65535):
    """Create a color. You should specify name, or RGB value."""

    if color:
        # Already color type :-)
        if isinstance(color, XColor):
            return color
        else:
            if color[0] == '#':
                return HexColor(colormap, color[1:], alpha)
            else:
                return NamedColor(colormap, color, alpha)
    else:
        return ValueColor(colormap, red, green, blue, alpha)
