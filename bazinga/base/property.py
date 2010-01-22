from object import Object
import signal

class Property(Object):

    """A property object."""

    class Set(signal.Signal):

        pass


    def __init__(self, docstring, default_value=None, readable=True, writable=True, deletable=False,
                 type=None, wcheck=None):

        self.__doc__ = docstring
        self.wcheck = wcheck
        self.readable = readable
        self.writable = writable
        self.deletable = deletable
        self.default_value = default_value
        self.type = type


    def __get__(self, inst, owner=None):

        if inst is None:
            return self
        if not self.readable:
            raise AttributeError("unreadable attribute")
        if self.__dict__.has_key(inst):
            return self.__dict__[inst]
        return self.default_value


    def __set__(self, inst, value):

        # Do not block initial set
        if self.__dict__.has_key(inst):
            if not self.writable:
                raise AttributeError("unwritable attribute")
        if self.wcheck:
            self.wcheck(inst, value)
        if self.type is not None and not isinstance(value, self.type):
            raise ValueError("value should be instance of {0}".format(self.type))
        self.__dict__[inst] = value
        self.emit_signal(self.Set, inst, value)


    def __delete__(self, inst):

        if not self.deletable:
            raise AttributeError("undeletable attribute")
        del self.__dict__[inst]


    def writecheck(self, func):

        self.wcheck = func
        return self


    def on_set(self, func):

        self.connect_signal(func, self.Set)
        return func
