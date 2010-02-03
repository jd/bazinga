from base.object import Object
from x import MainConnection

class Pixmap(Object):
    """Pixmap."""

    def __init__(self, depth, drawable, width=1, height=1):
        xid = MainConnection().generate_id()
        cp = MainConnection().core.CreatePixmapChecked(depth,
                                                       xid,
                                                       drawable,
                                                       width, height)
        cp.check()
        self.xid = xid

    def __del__(self):
        if hasattr(self, "xid"):
            MainConnection().core.FreePixmap(self.xid)
