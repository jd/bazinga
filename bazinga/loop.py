import pyev
from base.singleton import Singleton
from base.object import Object

class Loop(Object, pyev.Loop):

    """An event loop."""

    def __init__(self):
        pyev.Loop.__init__(pyev.EVFLAG_NOSIGFD)


class MainLoop(Singleton, Loop):
    
    """Bazinga main loop."""
    
    pass
