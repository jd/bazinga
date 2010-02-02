from base.singleton import SingletonPool
import weakref

class Event(object):
    pass

class KeyButtonEvent(Event, SingletonPool):
    def __init__(self, state, detail):
        self.state = state
        self.detail = detail

# Note:
# Each class has its own pool.
class KeyPress(KeyButtonEvent):
    _SingletonPool__instances = weakref.WeakValueDictionary()

class KeyRelease(KeyButtonEvent):
    _SingletonPool__instances = weakref.WeakValueDictionary()

class ButtonPress(KeyButtonEvent):
    _SingletonPool__instances = weakref.WeakValueDictionary()

class ButtonRelease(KeyButtonEvent):
    _SingletonPool__instances = weakref.WeakValueDictionary()
