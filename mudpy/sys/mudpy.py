"""This object represents the main context for the game. Objects in the game
will proxy events to this object in order to share state.

"""

from . import observer

class Mudpy(observer.Observer):
    """Mudpy object is used to attach initialization and start events."""

    def start(self):
        """Initializes components in the game and starts the server listening
        for connections.

        """

        from . import wireframe, calendar, server, client

        start_callback = server.initialize(self)
        calendar.initialize(self)
        client.initialize(self)
        wireframe.load_areas()
        start_callback(client.ClientFactory())
