"""Entry point for mud.py. Creates a server instance, parses config based on
arguments from the cli, assigns a configuration to the server and starts
listening on the configured port.

"""

from mudpy import server, debug, client, calendar, actor, wireframe, room
import sys, os

# data directory is for storing users, wireframes, and game details

__data__ = "data"

try:
    os.mkdir(__data__)
except IOError: # permissions error creating dir
    debug.log("create a writable \"data\" directory for mudpy to use",
            "error")
    raise
except OSError: # already exists
    pass

# load the wireframes depending on args passed to mud

try:
    wireframe.load(os.path.join(sys.argv[1], "wireframes"))
    wireframe.execute(os.path.join(sys.argv[1], "areas"))
except IndexError:
    debug.log("need to specify an initialization path", "error")
    raise
except IOError:
    debug.log("specified path does not exist: "+sys.argv[1], "error")
    raise

server.__instance__ = server.Instance()
calendar.load_calendar()

class Config:
    """Maintains configurations specific to the mud mudpy is running."""
    pass

# configuration values
server.__config__ = wireframe.apply(Config(), "server")
client.__config__ = wireframe.apply(Config(), "client")
calendar.__config__ = wireframe.apply(Config(), "calendar")
actor.__config__ = wireframe.apply(Config(), "actor")

# have the server start listening for connections
server.__instance__.start_listening(client.ClientFactory())
