from object import Object

class CachedProperty(object):
    """Cached Properties."""

    def __init__(self, name, getter, setter, deleter, doc):
        self.name = name
        self.getter = getter
        self.setter = setter
        self.deleter = deleter
        self.__doc__ = doc
        self.key = "_v_cached_property_value_%s" % name

    def __get__(self, inst, class_):
        if inst is None:
            return self

        value = getattr(inst, self.key, self)

        if value is not self:
            # We have a cached value
            return value

        # We need to compute and cache the value
        if self.getter:
            # Update cache
            value = self.getter(inst)
            # Returned nothing... see if cached has been updated
            if value is None:
                value = getattr(inst, self.key, self)
                if value is self:
                    # Getter did not set any value
                    raise AttributeError("Unable to fetch value for attribute '{0}' of '{1}'".format(self.name, inst))
        else:
            # No attribute value!
            raise AttributeError("Unable to fetch value for attribute '{0}' of '{1}'".format(self.name, inst))

        self.set_cache(inst, value)

        return value

    def __set__(self, inst, value):
        if self.setter:
            ret = self.setter(inst, value)
            if ret:
                value = ret
        setattr(inst, self.key, value)

    def __delete__(self, inst):
        if self.deleter:
            self.deleter(inst)
        self.del_cache(inst)

    def set_cache(self, inst, value):
        setattr(inst, self.key, value)
        # Emit signal if object is a Bazinga Object
        if isinstance(inst, Object):
            inst.emit_notify(self.name)

    def del_cache(self, inst):
        # Clear cache
        try:
            delattr(inst, self.key)
        except AttributeError:
            pass


class CachedPropertyType(CachedProperty):

    def __init__(self, name, bases=(), members={}):
        return super(CachedPropertyType, self).__init__(name,
                                                        members.get('__get__'),
                                                        members.get('__set__'),
                                                        members.get('__delete__'),
                                                        members.get('__doc__'))


cachedproperty = CachedPropertyType('cachedproperty')

def _ro_deleter(self):
    raise AttributeError("read-only attribute")


def _ro_setter(self, value):
    return _ro_deleter(self)


class RoCachedPropertyType(CachedProperty):

    def __init__(self, name, bases=(), members={}):
        return super(RoCachedPropertyType, self).__init__(name,
                                                          members.get('__get__'),
                                                          _ro_setter,
                                                          _ro_deleter,
                                                          members.get('__doc__'))

rocachedproperty = RoCachedPropertyType('rocachedproperty')
