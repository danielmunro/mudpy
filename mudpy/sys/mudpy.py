"""This object represents the main context for the game. Objects in the game
will proxy events to this object in order to share state.

"""

from . import observer, wireframe, calendar, server, client
from ..game.actor import actor

def proxy_listeners(*args):
    """Send messages to other modules in the framework. @todo do something
    about tight coupling.

    """

    calendar.proxy(*args)
    actor.proxy(*args)

class Mudpy(observer.Observer):
    """Mudpy object is used to attach initialization and start events."""

    def __init__(self):
        super(Mudpy, self).__init__()
        self.on("__any__", proxy_listeners)

    def start(self):
        """Initializes components in the game and starts the server listening
        for connections.

        """

        start_callback = server.initialize(self)
        calendar.initialize(self)
        actor.initialize(self)
        client.initialize(self)
        wireframe.load_areas()
        start_callback(client.ClientFactory())
