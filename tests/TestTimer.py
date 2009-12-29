#!/usr/bin/env python

import unittest

import Signal
from MainLoop import MainLoop
from Timer import Timer

class TestTimer(unittest.TestCase):

    def setUp(self):
        self.timer = Timer(1, 0)

    def test_timer(self):
        self.called = False
        self.timer.start()
        def cb(*args, **kw):
            self.called = True
        Signal.connect(cb, sender=self.timer, signal="timeout")
        MainLoop().loop()
        self.assert_(self.called)

if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
