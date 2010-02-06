from x import MainConnection, XObject

class Pixmap(XObject):
    """Pixmap."""

    def __init__(self, xid, autofree=True):
        self.autofree = autofree

    def free(self):
        MainConnection().core.FreePixmap(self)

    def __del__(self):
        if self.autofree:
            self.free()
