from base.singleton import SingletonPool
import window

import xcb.xproto
import weakref

class Event(object):

    @classmethod
    def convert(cls, xevent):
        """Convert an xcb.Event to a bazinga Event."""
        if cls._xevent_to_event.has_key(xevent.__class__):
            return cls._xevent_to_event[xevent.__class__].convert(xevent)

    @classmethod
    def convert_and_reemit(cls, sender, signal):
        """Convert an xcb.Event emitted  to a Bazinga event and reemit it."""
        converted = cls.convert(signal)
        if converted is not None:
            sender.emit_signal(converted)


class KeyButton(Event):
    def __init__(self, state, detail):
        self.state = state
        self.detail = detail

    @classmethod
    def convert(cls, xevent):
        event = cls(xevent.state, xevent.detail)
        event.x = xevent.event_x
        event.y = xevent.event_y
        event.root_x = xevent.root_x
        event.root_y = xevent.root_y
        return event


class Key(KeyButton):
    pass


class Button(KeyButton):
    pass

# Note:
# Each class has its own pool.
class KeyPress(Key, SingletonPool):
    _SingletonPool__instances = weakref.WeakValueDictionary()


class KeyRelease(Key, SingletonPool):
    _SingletonPool__instances = weakref.WeakValueDictionary()


class ButtonPress(Button, SingletonPool):
    _SingletonPool__instances = weakref.WeakValueDictionary()


class ButtonRelease(Button, SingletonPool):
    _SingletonPool__instances = weakref.WeakValueDictionary()


Event._xevent_to_event = {
    xcb.xproto.KeyPressEvent: KeyPress,
    xcb.xproto.KeyReleaseEvent: KeyRelease,
    xcb.xproto.ButtonPressEvent: ButtonPress,
    xcb.xproto.ButtonReleaseEvent: ButtonRelease,
}
