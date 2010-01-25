#!/usr/bin/env python

import unittest

from bazinga.base.object import Object

class TestObject(unittest.TestCase):

    def setUp(self):
        self.k = Object()

    def test_property(self):
        self.k.has_changed = False
        @self.k.on_notify("some_value")
        def x(sender, signal):
            sender.has_changed = True
        self.k.some_value = 1
        self.assert_(self.k.has_changed)


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
