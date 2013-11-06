"""This object represents the main context for the game. Objects in the game
will proxy events to this object in order to share state.

"""

from . import observer, wireframe, calendar, client, server
from ..game import room
from ..game.actor import actor

class Mudpy(observer.Observer):
    """Mudpy object is used to attach initialization and start events."""

    def __init__(self):
        self.path = ""
        self.events = None
        super(Mudpy, self).__init__()

    def proxy(self, *args):
        """This function is used as a callback to proxy messages from objects
        to the game.
        
        """

        self.fire(*args)

    def start(self):
        """Initializes components in the game and starts the server listening
        for connections.

        """

        wireframe.initialize(self)
        self.events = wireframe.create("event.mudpy").setup(self)
        server.initialize(self)
        calendar.initialize(self)
        actor.initialize(self)
        room.initialize()
        client.initialize()
        wireframe.start()
        server.start()
