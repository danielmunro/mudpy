"""Entry point for mud.py framework. Creates a main game observer object,
loads game areas, and starts the server listening for connections.

"""

from mudpy.sys import wireframe, observer, server

# Main game observer
__mudpy__ = observer.Observer()

# Load game areas
wireframe.load_areas()

# Start the server listening
server.start(__mudpy__)
