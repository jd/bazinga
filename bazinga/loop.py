import pyev
from basic import Singleton, Object

class Loop(Object, pyev.Loop):

    """An event loop."""

    def __init__(self):
        pyev.Loop.__init__(self, pyev.EVFLAG_NOSIGFD)


class MainLoop(Singleton, Loop):
    
    """Bazinga main loop."""
    
    pass
