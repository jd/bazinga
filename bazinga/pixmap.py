from x import MainConnection
from xobject import XObject, XID


class XPixmapID(XID):
    def __delete__(self):
        MainConnection().core.FreePixmap(self)


class Pixmap(XObject):
    """Pixmap."""

    def __init__(self, depth, drawable, width=1, height=1):
        xid = MainConnection().generate_id()
        cp = MainConnection().core.CreatePixmapChecked(depth,
                                                       xid,
                                                       drawable,
                                                       width, height)
        cp.check()
        self.xid = XPixmapID(xid)
