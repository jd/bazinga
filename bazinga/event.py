from base.singleton import SingletonPool
import weakref

class Event(object):
    pass

class KeyButton(Event, SingletonPool):
    def __init__(self, state, detail):
        self.state = state
        self.detail = detail

class Key(KeyButton):
    pass

class Button(KeyButton):
    pass

# Note:
# Each class has its own pool.
class KeyPress(Key):
    _SingletonPool__instances = weakref.WeakValueDictionary()

class KeyRelease(Key):
    _SingletonPool__instances = weakref.WeakValueDictionary()

class ButtonPress(Button):
    _SingletonPool__instances = weakref.WeakValueDictionary()

class ButtonRelease(Button):
    _SingletonPool__instances = weakref.WeakValueDictionary()
