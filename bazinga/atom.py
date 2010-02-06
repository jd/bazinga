from base.property import rocachedproperty
from base.singleton import SingletonPool


class Atom(SingletonPool, int):

    # Store Atoms for ever
    _SingletonPool__instances = {}

    class name(rocachedproperty):
        def __get__(self):
            from x import byte_list_to_str
            return byte_list_to_str(self.connection.core.GetAtomName(self).reply().name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{0} {1} ({2}) at 0x{3:x}>".format(self.__class__.__name__,
                                                   self.name,
                                                   int(self),
                                                   id(self))

    @staticmethod
    def __getpoolkey__(connection, name_or_value="Any"):
        return (id(connection), name_or_value)

    @classmethod
    def __getpool__(cls, connection, name_or_value="Any"):
        # We use the instances pool as:
        # (id(connection), atom name) = atom
        if isinstance(name_or_value, str):
            # Use standard lookup method
            return super(Atom, cls).__getpool__(connection, name_or_value)
        else:
            # Iter on all atom, and as soon as we find something, return it
            for k, v in cls._SingletonPool__instances.iteritems():
                if k[0] == id(connection) and v == name_or_value:
                    return v
            else:
                raise LookupError

    @classmethod
    def __setpool__(cls, obj, connection, name_or_value):
        cls._SingletonPool__instances[cls.__getpoolkey__(connection, obj.name)] = obj

    def __new__(cls, connection, name_or_value="Any"):
        if isinstance(name_or_value, str):
            ia = connection.core.InternAtom(False,
                                            len(name_or_value),
                                            name_or_value)
            self = super(Atom, cls).__new__(cls, ia.reply().atom)
            Atom.name.set_cache(self, name_or_value)
        else:
            self = super(Atom, cls).__new__(cls, name_or_value)
        # We need to store it now, because __setpool__ we need it
        self.connection = connection
        return self
