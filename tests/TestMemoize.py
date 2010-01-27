#!/usr/bin/env python

import unittest

from bazinga.base.memoize import memoize

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


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
