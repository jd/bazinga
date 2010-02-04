from base.property import rocachedproperty
from base.object import Object
from base.singleton import SingletonPool

import xcb.xproto

class Atom(Object, SingletonPool):
    """X atom."""

    # Keep references for ever.
    # That should be a LRU in the future, or it may grow too large.
    _SingletonPool__instances = dict()

    class value(rocachedproperty):
        """X atom value."""
        def __get__(self):
            value = self._cookie.reply().atom
            del self._cookie
            return value

    class name(rocachedproperty):
        def __get__(self):
            from x import byte_list_to_str
            value = byte_list_to_str(self._cookie.reply().name)
            del self._cookie
            return value

    def __init__(self, name_or_value="Any"):
        from x import MainConnection
        if name_or_value.__class__ == str:
            Atom.name.set_cache(self, name_or_value)
            try:
                Atom.value.set_cache(self, getattr(xcb.xproto.Atom, self.name))
            except AttributeError:
                self._cookie = MainConnection().core.InternAtom(False,
                                                                len(self.name),
                                                                self.name)
        else:
            Atom.value.set_cache(self, name_or_value)
            for atom_name, atom_value in xcb.xproto.Atom.__dict__.items():
                if self.value == atom_value:
                    Atom.name.set_cache(self, atom_name)
                    break
            else:
                self._cookie = MainConnection().core.GetAtomName(self.value)
