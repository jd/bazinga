import base.signal

class Event(base.signal.Signal):
    pass

class KeyButtonEvent(Event):
    def __init__(self, xevent):
        self.detail = xevent.detail
        self.state = xevent.state
        self.root_x = xevent.root_x
        self.root_y = xevent.root_y
        self.x = xevent.event_x
        self.y = xevent.event_y

class KeyPress(KeyButtonEvent):
    pass

class KeyRelease(KeyButtonEvent):
    pass

class ButtonPress(KeyButtonEvent):
    pass

class ButtonRelease(KeyButtonEvent):
    pass
