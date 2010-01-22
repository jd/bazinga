#!/usr/bin/env python

import unittest

from bazinga.base.object import Object

class TestTimer(unittest.TestCase):

    def test_new_signal(self):
        self.called = False
        @Object.on_new
        def cb(*args, **kw):
            self.called = True
        Object()
        self.assert_(self.called)

if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
