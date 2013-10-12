"""Entry point for mud.py. Creates a server instance, parses config based on
arguments from the cli, assigns a configuration to the server and starts
listening on the configured port.

"""

from mudpy import server, debug, client, calendar, actor, wireframe, config
import sys, os, yaml

# data directory is for storing users and game state

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
    wireframe.path = sys.argv[1]
except IndexError:
    debug.log("need to specify an initialization path", "error")
    raise

server.__instance__ = server.Instance()

try:
    wireframe.execute()
except IOError:
    debug.log("specified path does not exist: "+wireframe.path, "error")
    raise

calendar.load(server)

# configuration values
server.__config__ = wireframe.create("config.server")
client.__config__ = wireframe.create("config.client")
calendar.__config__ = wireframe.create("config.calendar")
actor.__config__ = wireframe.create("config.actor")

# have the server start listening for connections
server.__instance__.start_listening(client.ClientFactory())
