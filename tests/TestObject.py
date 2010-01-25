#!/usr/bin/env python

import unittest

from bazinga.base.object import Object

class TestObject(unittest.TestCase):

    def setUp(self):
        self.k = Object()

    def test_property(self):
        self.k.has_changed = False
        def x(sender, signal):
            self.assert_(signal.value == "some_value")
            sender.has_changed = True
        self.k.connect_notify(x, "some_value")
        self.k.some_value = 1
        self.assert_(self.k.has_changed)


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
