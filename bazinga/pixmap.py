from x import MainConnection, XObject

class XPixmap(XObject):
    """X Pixmap."""

class Pixmap(XPixmap):
    """Bazinga pixmap.
    This one is autocollected from X when you do not use it anymore."""

    def __del__(self):
        MainConnection().core.FreePixmap(self)
        super(Pixmap, self).__del__()
