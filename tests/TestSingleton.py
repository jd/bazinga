#!/usr/bin/env python

import unittest

from bazinga.basic import Singleton

class TestBasicObject(unittest.TestCase):

    def test_identity(self):
        self.assert_(Singleton() is Singleton())

if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
