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
    pass

class KeyRelease(Key, SingletonPool):
    pass

class ButtonPress(Button, SingletonPool):
    pass

class ButtonRelease(Button, SingletonPool):
    pass
