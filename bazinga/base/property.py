ncaches = 0L

class CachedProperty(object):
    """Cached Properties."""

    def __init__(self, getter, setter, deleter, doc):
        self.getter = getter
        self.setter = setter
        self.deleter = deleter
        self.__doc__ = doc
        global ncaches
        ncaches += 1
        self.key = "_v_cached_property_value_%d" % ncaches

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
            self.getter(inst)
            value = getattr(inst, self.key, self)
            if value is self:
                # Getter did not set any value
                raise AttributeError
        else:
            # No attribute value!
            raise AttributeError

        setattr(inst, self.key, value)

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
        # Clear cache
        try:
            delattr(inst, self.key)
        except AttributeError:
            pass

    def set_cache(self, inst, value):
        setattr(inst, self.key, value)


class CachedPropertyType(CachedProperty):

    def __init__(self, name, bases=(), members={}):
        return super(CachedPropertyType, self).__init__(members.get('__get__'),
                                                        members.get('__set__'),
                                                        members.get('__delete__'),
                                                        members.get('__doc__'))

cachedproperty = CachedPropertyType('cachedproperty')
