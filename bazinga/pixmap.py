from x import MainConnection
from xobject import XObject

class Pixmap(XObject):
    """Pixmap."""

    def __new__(cls, *args, **kwargs):
        return super(Pixmap, cls).__new__(cls, MainConnection().generate_id())

    def __init__(self, depth, drawable, width=1, height=1):
        MainConnection().core.CreatePixmapChecked(depth,
                                                  self,
                                                  drawable,
                                                  width, height).check()

    def __del__(self):
        MainConnection().core.FreePixmap(self)
