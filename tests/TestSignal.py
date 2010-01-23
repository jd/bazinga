#!/usr/bin/env python

import unittest

import bazinga.base.signal as signal
from bazinga.base.object import Object

class TestSignal(unittest.TestCase):
    class Yack(Object):
        """A subclass of Object. That's all."""
        pass

    def set_changed(self, signal):
        self.has_changed = True


    def _test_sender(self, sender, sender_to_listen):
        self.has_changed = False
        signal.connect(self.set_changed, signal="yo", sender=sender_to_listen)
        signal.emit(signal="yo", sender=sender)
        self.assert_(self.has_changed)
        signal.disconnect(self.set_changed, signal="yo", sender=sender_to_listen)

    def test_sender_on_class(self):
        self._test_sender(self.Yack(), self.Yack)

    def test_sender_on_parent_class(self):
        self._test_sender(self.Yack(), Object)

    def test_sender_on_object(self):
        y = self.Yack()
        self._test_sender(y, y)


    def _test_signal(self, signal_to_emit, signal_to_listen):
        self.has_changed = False
        obj = Object()
        obj.connect_signal(self.set_changed, signal_to_listen)
        obj.emit_signal(signal_to_emit)
        self.assert_(self.has_changed)
        obj.disconnect_signal(self.set_changed, signal_to_listen)

    def test_signal_on_class(self):
        self._test_signal(self.Yack(), self.Yack)

    def test_signal_on_parent_class(self):
        self._test_signal(self.Yack(), Object)

    def test_signal_on_object(self):
        y = self.Yack()
        self._test_signal(y, y)


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
