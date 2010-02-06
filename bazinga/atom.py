from base.property import rocachedproperty
from x import XObject
from base.singleton import SingletonPool


class Atom(SingletonPool, XObject):

    # Store Atoms for ever
    _SingletonPool__instances = {}

    class name(rocachedproperty):
        def __get__(self):
            from x import MainConnection, byte_list_to_str
            return byte_list_to_str(MainConnection().core.GetAtomName(self).reply().name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self.name)

    @staticmethod
    def __getpoolkey__(name_or_value="Any"):
        return name_or_value

    @classmethod
    def __getpool__(cls, name_or_value="Any"):
        if isinstance(name_or_value, str):
            return super(Atom, cls).__getpool__(cls, name_or_value)
        else:
            for v in cls._SingletonPool__instances.itervalues():
                if v == name_or_value:
                    return v
            else:
                raise LookupError

    @classmethod
    def __setpool__(cls, obj, *args, **kwargs):
        cls._SingletonPool__instances[obj.name] = obj

    def __new__(cls, name_or_value="Any"):
        if isinstance(name_or_value, str):
            from x import MainConnection
            ia = MainConnection().core.InternAtom(False,
                                                  len(name_or_value),
                                                  name_or_value)
            self = super(Atom, cls).__new__(cls, ia.reply().atom)
            Atom.name.set_cache(self, name_or_value)
        else:
            self = super(Atom, cls).__new__(cls, name_or_value)
        return self
