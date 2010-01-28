#!/usr/bin/env python

import unittest

from bazinga.base.property import cachedproperty, rocachedproperty


class TestCachedProperty(unittest.TestCase):

    class Phone(object):

        class number(cachedproperty):
            pass

        class name(cachedproperty):
            def __get__(self):
                return "Morcheeba"
            def __set__(self, value):
                return value + "!"

        class roprop(rocachedproperty):
            pass

    def setUp(self):
        self.p = self.Phone()

    def test_simple_caching(self):
        self.Phone.number.set_cache(self.p, 1)
        self.assert_(self.p.number == 1)

    def test_get(self):
        self.assert_(self.p.name == "Morcheeba")

    def test_set(self):
        self.p.name = "Nirvana"
        self.assert_(self.p.name == "Nirvana!")

    def test_del(self):
        self.p.name = "Nirvana"
        del self.p.name
        self.assert_(self.p.name == "Morcheeba")

    def test_set_cache(self):
        self.Phone.name.set_cache(self.p, "Clash...")
        self.assert_(self.p.name == "Clash...")

    def test_ro_property(self):
        try:
            self.p.roprop = 2
            self.assert_(False) # never reached
        except AttributeError:
            pass

        try:
            del self.p.roprop
            self.assert_(False) # never reached
        except AttributeError:
            pass

if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
