#!/usr/bin/env python

import unittest

from bazinga.base.memoize import memoize, Memoized

class TestMemoize(unittest.TestCase):

    def test_memoize(self):

        @memoize()
        def memoized_func(x, y=1):

            self.executed += 1
            return x + y

        self.executed = 0

        self.assert_(memoized_func(1, 3) == 4)
        self.assert_(self.executed == 1)
        self.assert_(memoized_func(1, 3) == 4)
        self.assert_(self.executed == 1)
        self.assert_(memoized_func(1, y=4) == 5)
        self.assert_(self.executed == 2)
        self.assert_(memoized_func(1, y=4) == 5)
        self.assert_(self.executed == 2)

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
