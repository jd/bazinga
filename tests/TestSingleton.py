#!/usr/bin/env python

import unittest

from bazinga.base.singleton import Singleton, SingletonPool

class TestSingleton(unittest.TestCase):

    def test_singleton_identity(self):
        self.assert_(Singleton() is Singleton())

    def test_singleton_pool_identify(self):
        self.assert_(SingletonPool(1, 2) is not SingletonPool(1, 3))
        self.assert_(SingletonPool(1, 2) is SingletonPool(1, 2))


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
