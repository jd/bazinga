from base.object import Object

class XObject(Object, int):
    # Use default format from object rather than from int
    __str__ = object.__str__
