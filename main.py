"""Entry point for mud.py framework. Creates a main game observer object,
loads game areas, and starts the server listening for connections.

"""

import sys
from mudpy.sys import wireframe, debug, observer, server, client

# Main game observer
__mudpy__ = observer.Observer()

# Load game areas
wireframe.load_areas()

# Start the server listening
server.start(client.ClientFactory())
