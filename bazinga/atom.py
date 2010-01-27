from base.memoize import memoize, Memoized
from base.object import Object
from x import MainConnection

import xcb.xproto

class XAtom(Object, Memoized):
    """X Atom."""

    def __init__(self, name="Any"):
        try:
            self._value = getattr(xcb.xproto.Atom, name)
        except AttributeError:
            # No pre-defined atom by that name
            self._cookie = MainConnection().core.InternAtom(False, len(name), name)

    def read_reply(self):
        if hasattr(self, "_cookie"):
            self._value = self._cookie.reply().atom
            del self._cookie

    @property
    def value(self):
        self.read_reply()
        return self._value

def Atom(*args, **kwargs):
    return XAtom(*args, **kwargs).value
