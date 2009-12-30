import pyev
from bazinga.basic import Singleton

class MainLoop(Singleton, pyev.Loop):

    def __init__(self):
        Singleton.__init__(self)
        pyev.Loop.__init__(pyev.EVFLAG_NOSIGFD)
