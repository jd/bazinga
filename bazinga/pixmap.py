from x import XObject

class XPixmap(XObject):
    """X Pixmap."""

    @classmethod
    def create(cls, connection, depth, drawable, width, height):
        xpixmap = super(XPixmap, cls).create(connection)
        xpixmap.connection.core.CreatePixmapCheced(depth,
                                                   xpixmap,
                                                   drawable,
                                                   width,
                                                   height).check()
        return xpixmap


class Pixmap(XPixmap):
    """Bazinga pixmap.
    This one is autocollected from X when you do not use it anymore."""

    def __del__(self):
        self.connection.core.FreePixmap(self)
        super(Pixmap, self).__del__()
