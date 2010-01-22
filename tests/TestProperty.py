#!/usr/bin/env python

import unittest

from bazinga.base.property import Property
from bazinga.base.object import Object

class TestProperty(unittest.TestCase):

    class Phone(object):

        nodefaultval = Property("")
        defaultval = Property("", 1)
        ro = Property("", 42, writable=False)
        rw = Property("", 43, readable=False, deletable=True)
        notdeletable = Property("", deletable=False)
        typed = Property("", type=str)

        @defaultval.writecheck
        def defaultval_writecheck(self, newvalue):
            if newvalue == 666:
                raise ValueError("EVIL")


    def setUp(self):

        self.p = self.Phone()


    def test_defaultval(self):

        self.assert_(self.p.nodefaultval == None)
        self.assert_(self.p.defaultval == 1)


    def test_ro(self):

        self.assert_(self.p.ro is 42)
        self.p.ro = 42
        try:
            self.p.ro = 43
            self.assert_(False) # never reached
        except AttributeError:
            pass


    def test_rw(self):

        try:
            print self.p.rw
            self.assert_(False) # never reached
        except AttributeError:
            pass

        self.p.rw = 1
        self.p.rw = 2
        del self.p.rw


    def test_del(self):

        self.p.notdeletable = 23
        try:
            del self.p.notdeletable
            self.assert_(False) # never reached
        except AttributeError:
            pass


    def test_check(self):

        self.p.defaultval = 34
        try:
            self.p.defaultval = 666
            self.assert_(False) # never reached
        except ValueError:
            pass


    def test_signal(self):

        self.has_signal = False

        @self.Phone.defaultval.on_set
        def on_set(inst, newvalue, sender=None):
            print inst
            inst.has_signal = True

        self.p.defaultval = 999
        self.assert_(self.p.has_signal)


    def test_typecheck(self):
        self.p.typed = "lol"

        try:
            self.p.typed = 23
            self.assert_(False) # never reached
        except ValueError:
            pass


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
