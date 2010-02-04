from base.object import Object

class XObject(Object, int):
    def __init__(self, xid):
        super(XObject, self).__init__()
