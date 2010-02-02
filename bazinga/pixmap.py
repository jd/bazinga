from base.object import Object
from x import MainConnection

class Pixmap(Object):
    """Pixmap."""

    def __init__(self, depth, drawable, width, height):
        self.xid = MainConnection().generate_id()
        # XXX roots[0]...
        MainConnection().core.CreatePixmap(MainConnection.roots[0].root_depth,
                                           self.xid,
                                           drawable
