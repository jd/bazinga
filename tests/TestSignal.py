#!/usr/bin/env python

import unittest

import bazinga.base.signal as signal
from bazinga.base.object import Object

class TestSignal(unittest.TestCase):

    class Yack(Object):

        """A subclass of Object. That's all."""

        pass


    def _test_setattr_signal_with_sender(self, obj, sender):

        def f():
            self.has_changed = True

        self.has_changed = False
        signal.connect(f, signal="yo", sender=sender)
        obj.emit_signal("yo")
        self.assert_(self.has_changed)
        signal.disconnect(f, signal="yo", sender=sender)


    def test_setattr_signal_on_class(self):

        self._test_setattr_signal_with_sender(self.Yack(), self.Yack)


    def test_setattr_signal_on_parent_class(self):

        self._test_setattr_signal_with_sender(self.Yack(), Object)


    def test_setattr_signal_on_object(self):

        y = self.Yack()
        self._test_setattr_signal_with_sender(y, y)


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
