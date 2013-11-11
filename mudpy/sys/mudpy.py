"""This object represents the main context for the game. Objects in the game
will proxy events to this object in order to share state.

"""

from . import observer, wireframe, event, calendar, server, client
from ..game.actor import actor

class Mudpy(observer.Observer):
    """Mudpy object is used to attach initialization and start events."""

    def __init__(self):
        super(Mudpy, self).__init__()
        self.on("__any__", self._proxy_listeners)

    def proxy(self, *args):
        """This function is used as a callback to proxy messages from objects
        to the game.
        
        """

        self.fire(*args)

    def start(self):
        """Initializes components in the game and starts the server listening
        for connections.

        """

        server_instance = server.Instance(self)
        calendar_instance = calendar.initialize(self)
        actor.initialize(self)
        wireframe.load_areas()
        server_instance.start(client.ClientFactory())

    def _proxy_listeners(self, *args):
        calendar.proxy(*args)
        actor.proxy(*args)
