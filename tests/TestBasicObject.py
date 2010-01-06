#!/usr/bin/env python

import unittest

import bazinga.signal as signal
from bazinga.basic import Object, Setattr

class TestBasicObject(unittest.TestCase):

    class Yack(Object):

        """A subclass of Object. That's all."""

        pass

    def _test_setattr_signal_with_sender(self, obj, sender):
        def f(field, oldvalue, newvalue):
            self.assert_(field == "value")
            self.has_changed = True

        self.has_changed = False
        signal.connect(f, signal=Setattr, sender=sender)
        obj.value = 42
        self.assert_(self.has_changed)
        signal.disconnect(f, signal=Setattr, sender=sender)

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
