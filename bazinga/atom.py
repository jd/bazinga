from base.memoize import Memoized
from base.property import rocachedproperty
from base.object import Object
from x import MainConnection

import xcb.xproto

class Atom(Object, Memoized):
    """X atom."""

    def __init__(self, name="Any"):
        self.name = name
        try:
            Atom.value.set_cache(self, getattr(xcb.xproto.Atom, name))
        except AttributeError:
            self._cookie = MainConnection().core.InternAtom(False,
                                                            len(name),
                                                            name)

    class value(rocachedproperty):
        """X atom value."""

        def __get__(self):
            value = self._cookie.reply().atom
            del self._cookie
            return value
