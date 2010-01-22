#!/usr/bin/env python

import unittest

from bazinga.base.singleton import Singleton

class TestProperty(unittest.TestCase):

    def test_identity(self):
        self.assert_(Singleton() is Singleton())

if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
