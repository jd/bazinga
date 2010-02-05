#!/usr/bin/env python

import unittest

from bazinga.base.singleton import Singleton, SingletonPool

class TestSingleton(unittest.TestCase):

    class Point(SingletonPool):
        _SingletonPool__instances = {}
        def __init__(self, x, y):
            pass

    def test_singleton_identity(self):
        self.assert_(Singleton() is Singleton())

    def test_singleton_pool_identify(self):
        self.assert_(self.Point(1, 2) is not self.Point(1, 3))
        self.assert_(self.Point(1, 2) is self.Point(1, 2))


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
