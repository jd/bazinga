import pyev
from basic import Singleton

class Loop(pyev.Loop):

    """An event loop."""

    def __init__(self):
        pyev.Loop.__init__(pyev.EVFLAG_NOSIGFD)


class MainLoop(Singleton, Loop):
    
    """Bazinga main loop."""
    
    pass
