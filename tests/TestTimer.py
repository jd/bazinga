#!/usr/bin/env python

import unittest

import bazinga.signal
from bazinga.loop import MainLoop
from bazinga.timer import Timer

class TestTimer(unittest.TestCase):

    def setUp(self):
        self.timer = Timer(0.1, 0)

    def test_timer(self):
        self.called = False
        self.timer.start()
        def cb(*args, **kw):
            self.called = True
        bazinga.signal.connect(cb, sender=self.timer, signal=self.timer.Timeout)
        MainLoop().loop()
        self.assert_(self.called)

if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
