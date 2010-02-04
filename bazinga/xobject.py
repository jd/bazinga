from base.object import Object

class XObject(Object):
    def __init__(self, xid):
        self.xid = xid

    def __int__(self):
        return self.xid
