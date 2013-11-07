"""This object represents the main context for the game. Objects in the game
will proxy events to this object in order to share state.

"""

from . import observer, wireframe, event

class Mudpy(observer.Observer):
    """Mudpy object is used to attach initialization and start events."""

    def __init__(self, path):
        wireframe.__path__ = path
        wireframe.preload()
        super(Mudpy, self).__init__()
        self.events = wireframe.create("event.mudpy").setup(self)

    def proxy(self, *args):
        """This function is used as a callback to proxy messages from objects
        to the game.
        
        """

        self.fire(*args)

    def start(self):
        """Initializes components in the game and starts the server listening
        for connections.

        """

        from . import calendar, server, client
        from ..game.actor import actor

        server_instance = server.Instance(self)
        calendar_instance = calendar.initialize()
        wireframe.load_areas()
        server_instance.start(client.ClientFactory())

    def _proxy_listeners(self, *args):
        from . import calendar
        from ..game.actor import actor
        calendar.proxy(*args)
        actor.proxy(*args)
