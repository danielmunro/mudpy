from . import observer

class Mudpy(observer.Observer):
    """Mudpy object is used to attach initialization and start events."""
    def __init__(self):
        self.observers = {}
        self.path = ""
        self.events = None
        self.on("start", self.load_events)

    def load_events(self, _event = None):
        from . import wireframe, event
        self.events = wireframe.create("event.mudpy").setup(self)

    def proxy(self, *args):
        """This function is used as a callback to proxy messages from game
        objects to mudpy.
        
        """

        self.fire(*args)
