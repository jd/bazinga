#!/usr/bin/env python

import unittest

import bazinga.signal as signal
from bazinga.basic import Object, Setattr

class TestBasicObject(unittest.TestCase):

    class Yack(Object):

        """A subclass of Object. That's all."""

        def __setattr_weirdo__(self, oldvalue, newvalue):

            if oldvalue == 1:
                raise ValueError


    def _test_setattr_signal_with_sender(self, obj, sender):
        def f(field, oldvalue, newvalue):
            self.assert_(field == "value")
            self.has_changed = True

        self.has_changed = False
        signal.connect(f, signal=Setattr, sender=sender)
        obj.value = 42
        self.assert_(self.has_changed)
        signal.disconnect(f, signal=Setattr, sender=sender)
        self.has_changed = False
        obj.value = 42
        self.assert_(not self.has_changed)

    def test_setattr_signal_on_class(self):
        self._test_setattr_signal_with_sender(self.Yack(), self.Yack)

    def test_setattr_signal_on_parent_class(self):
        self._test_setattr_signal_with_sender(self.Yack(), Object)

    def test_setattr_signal_on_object(self):
        y = self.Yack()
        self._test_setattr_signal_with_sender(y, y)

    def test_setattr_raise(self):
        y = self.Yack()
        y.weirdo = 1
        try:
            y.weirdo = 2
            print y.weirdo
            self.assert_(False) # should not be executed
        except ValueError:
            pass


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
