#!/usr/bin/env python

import unittest

from bazinga.base.singleton import Singleton, Memoized

class TestSingleton(unittest.TestCase):

    def test_singleton_identity(self):
        self.assert_(Singleton() is Singleton())

    def test_memoized_identity(self):
        self.assert_(Memoized() is Memoized())

    def test_memoized_subclass_identity(self):
        class Mouse(Memoized):
            def __init__(self, bla):
                pass

        self.assert_(Mouse(1) is Mouse(1))
        self.assert_(Mouse(1) is not Mouse(2))
        self.assert_(Mouse(2) is Mouse(2))


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
