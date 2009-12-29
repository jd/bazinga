import xpyb
from xcb.xproto import *

class X(object):
    def __init__(self):
        self.connection = xcb.connect()
