import xcb.xproto
import weakref

from base.object import Object
from base.property import rocachedproperty
from base.singleton import SingletonPool

class XColor(Object):
    """Generic color class."""

    class pixel(rocachedproperty):
        """Pixel value of the color."""
        pass

    class red(rocachedproperty):
        """Red value of the color."""
        pass

    class green(rocachedproperty):
        """Green value of the color."""
        pass

    class blue(rocachedproperty):
        """Blue value of the color."""
        pass

    class alpha(rocachedproperty):
        """Alpha value of the color."""
        pass

    def __hex__(self):
        return "#{0:<02x}{1:<02x}{2:<02x}{3:<02x}".format(self.red / 257,
                                                          self.green / 257,
                                                          self.blue / 257,
                                                          self.alpha / 257)

    def __init__(self, connection):
        self.connection = connection

    @property
    def name(self):
        """Name of the color."""
        return hex(self)

    def __str__(self):
        return self.name


class NamedColor(XColor):
    """A named color."""

    _SingletonPool__instances = {}

    @staticmethod
    def __getpoolkey__(connection, colormap, name, alpha=65535):
        return (id(connection), colormap, name, alpha)

    class name(rocachedproperty):
        __doc__  = XColor.name.__doc__

    def __init__(self, connection, colormap, name, alpha=65535):
        if alpha < 0 or alpha > 65535:
            raise ValueError("Bad alpha value.")

        cookie = connection.core.AllocNamedColor(colormap, len(name), name)
        NamedColor.name.set_cache(self, name)
        NamedColor.alpha.set_cache(self, alpha)

        reply = cookie.reply()
        NamedColor.red.set_cache(self, reply.exact_red)
        NamedColor.green.set_cache(self, reply.exact_green)
        NamedColor.blue.set_cache(self, reply.exact_blue)
        NamedColor.pixel.set_cache(self, reply.pixel)

        super(NamedColor, self).__init__(connection)


class ValueColor(XColor, SingletonPool):
    """A color by value."""

    _SingletonPool__instances = {}

    @staticmethod
    def __getpoolkey__(connection, colormap, red=0, green=0, blue=0, alpha=65535):
        return (id(connection), colormap, red, green, blue, alpha)

    def __init__(self, connection, colormap, red=0, green=0, blue=0, alpha=65535):

        for value in [ red, blue, green, alpha ]:
            if value < 0 or value > 65535:
                raise ValueError("Color attribute value is too high.")

        cookie = connection.core.AllocColor(colormap, red, green, blue)
        ValueColor.alpha.set_cache(self, alpha)

        reply = cookie.reply()
        ValueColor.red.set_cache(self, reply.red)
        ValueColor.green.set_cache(self, reply.green)
        ValueColor.blue.set_cache(self, reply.blue)
        ValueColor.pixel.set_cache(self, reply.pixel)

        super(ValueColor, self).__init__(connection)


def Color(connection, colormap, color=None, red=0, green=0, blue=0, alpha=65535):
    """Create a color. You should specify name, or RGBA values."""
    if color:
        # Already color type :-)
        if isinstance(color, XColor):
            return color
        elif color[0] == '#':
            len_name = len(color)

            if len_name != 7 and len_name != 9:
                raise ValueError("Bad color name {0}.".format(color))

            red = int(color[2:4], 16) * 257
            green = int(color[4:6], 16) * 257
            blue = int(color[6:8], 16) * 257

            if len_name == 9:
                alpha = int(color[8:10], 16) * 257
        else:
            return NamedColor(connection, colormap, color, alpha)
    return ValueColor(connection, colormap, red, green, blue, alpha)
