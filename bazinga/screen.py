from base.object import Object
from base.property import rocachedproperty

import xcb.xproto


class Screen(Object, int):

    class x(rocachedproperty):
        def __get__(self):
            return 0

    class y(rocachedproperty):
        def __get__(self):
            return 0

    class width(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    class height(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    class outputs(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    def __new__(cls, connection, xid, root):
        return super(Screen, cls).__new__(cls, xid)

    def __init__(self, connection, xid, root):
        self.connection = connection
        self.root = root

    def __repr__(self):
        return "<{0} {1} at 0x{2:x}>".format(self.__class__.__name__,
                                             int(self), id(self))

    def _retrieve_info(self):
        for root in self.connection.get_setup().roots:
            if root == self.root:
                Screen.width.set_cache(self, root.width_in_pixels)
                Screen.height.set_cache(self, root.height_in_pixels)
                output = Output()
                Output.width_mm.set_cache(output, root.width_in_millimeters)
                Output.height_mm.set_cache(output, root.height_in_millimeters)
                Screen.outputs.set_cache(self, [ output ])
                break


class ScreenXinerama(Screen):
    pass


class ScreenRandr(Screen):
    """A screen."""

    class x(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    class y(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    class width(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    class height(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    class outputs(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    def _retrieve_info(self):
        reply = self.connection.randr.GetCrtcInfo(self,
                                                  xcb.xproto.Time.CurrentTime).reply()
        Screen.outputs.set_cache(self,
                                 [ OutputRandr(self.connection, xid) for xid in
                                   reply.outputs ])
        Screen.x.set_cache(self, reply.x)
        Screen.y.set_cache(self, reply.y)
        Screen.width.set_cache(self, reply.width)
        Screen.height.set_cache(self, reply.height)


class Output(Object):
    class width_mm(rocachedproperty):
        pass

    class height_mm(rocachedproperty):
        pass


class OutputRandr(Output, int):
    """A screen output."""

    class name(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    class width_mm(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    class height_mm(rocachedproperty):
        def __get__(self):
            return self._retrieve_info()

    def __new__(cls, connection, xid):
        return super(OutputRandr, cls).__new__(cls, xid)

    def __init__(self, connection, xid):
        self.connection = connection

    def _retrieve_info(self):
        info = self.connection.randr.GetOutputInfo(self,
                                                   xcb.xproto.Time.CurrentTime).reply()
        from x import byte_list_to_str
        self.__class__.name.set_cache(self, byte_list_to_str(info.name))
        self.__class__.width_mm.set_cache(self, info.mm_width)
        self.__class__.height_mm.set_cache(self, info.mm_height)

    def __repr__(self):
        return "<{0} {1} at 0x{2:x}>".format(self.__class__.__name__,
                                             int(self), id(self))
