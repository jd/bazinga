import basic

class Window(basic.Object):

    """A basic X window."""

    def __init__(self, id):

        """Initialize a X window. window_id must be a valid X id resource."""

        self.id = id
