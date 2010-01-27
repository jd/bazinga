from base.memoize import Memoized
from base.property import cachedproperty
from base.object import Object
from x import MainConnection

import xcb.xproto

class XAtom(Object, Memoized):
    """X atom."""

    def __init__(self, name="Any"):
        self.name = name

    class value(cachedproperty):
        """X atom value."""

        def __get__(self):
            try:
                return getattr(xcb.xproto.Atom, self.name)
            except AttributeError:
                # No pre-defined atom by that name
                return MainConnection().core.InternAtom(False,
                                                        len(self.name),
                                                        self.name).reply().atom

        def __set__(self):
            raise AttributeError("read-only attribute")


def Atom(name):
    """Get an XAtom value directly.
    This function is a wrapper to XAtom class.
    This will return a value you can directly use to feed XCB functions."""
    return XAtom(name).value
