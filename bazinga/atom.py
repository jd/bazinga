from base.property import rocachedproperty
from base.singleton import SingletonPool
from xobject import XObject


class Atom(SingletonPool, XObject):
    """X atom."""

    # Keep references for ever.
    # That should be a LRU in the future, or it may grow too large.
    _SingletonPool__instances = {}

    class name(rocachedproperty):
        pass

    @staticmethod
    def __pool_key__(name=None, xid=None):
        return name or xid

    def __init__(self, name=None, xid=None):
        # Ok, this code is not async, but really, I doubt it's worh the effort.
        from x import MainConnection
        xid = xid or MainConnection().core.InternAtom(False, len(name), name).reply().atom

        name = name or MainConnection().core.GetAtomName(xid).reply().name
        Atom.name.set_cache(self, name)

        XObject.__init__(self, xid)
        SingletonPool.__init__(self)
