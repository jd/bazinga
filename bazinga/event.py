from base.singleton import SingletonPool
import weakref

class Event(object):
    pass

class KeyButton(Event):
    def __init__(self, state, detail):
        self.state = state
        self.detail = detail

class Key(KeyButton):
    pass

class Button(KeyButton):
    pass

# Note:
# Each class has its own pool.
class KeyPress(Key, SingletonPool):
    __SingletonPool_instances = weakref.WeakValueDictionary()

class KeyRelease(Key, SingletonPool):
    __SingletonPool_instances = weakref.WeakValueDictionary()

class ButtonPress(Button, SingletonPool):
    __SingletonPool_instances = weakref.WeakValueDictionary()

class ButtonRelease(Button, SingletonPool):
    __SingletonPool_instances = weakref.WeakValueDictionary()
