from base.memoize import Memoized
from base.property import cachedproperty
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

    class value(cachedproperty):
        """X atom value."""

        def __get__(self):
            return self._cookie.reply().atom

        def __set__(self):
            raise AttributeError("read-only attribute")

        def __delete__(self):
            raise AttributeError("undeletable attribute")
