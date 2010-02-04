from base.object import Object


class XID(int):
    def __init__(self, xid):
        self.xid = xid

    def __int__(self):
        return self.xid
    __long__ = __int__


class XObject(Object):
    def __int__(self):
        return self.xid
    __long__ = __int__
