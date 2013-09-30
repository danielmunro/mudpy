"""Entry point for mud.py. Creates a server instance, parses config based on
arguments from the cli, assigns a configuration to the server and starts
listening on the configured port.

"""

from mudpy import server, debug, client, calendar, actor, wireframe
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
    wireframe.load(sys.argv[1])
except IndexError:
    path = os.path.join(__data__, "wireframes.yaml")
    if os.path.exists(path):
        wireframe.repersist(path)
    else:
        debug.log("need to specify an initialization path", "error")
        raise
except IOError:
    debug.log("specified path does not exist: "+sys.argv[1], "error")
    raise

def update_wireframe():
    wireframe.save(__data__)

server.__instance__ = server.Instance()
server.__instance__.heartbeat.attach('tick', update_wireframe)
calendar.load_calendar()

# configuration values
server.__config__ = wireframe.new("server")
client.__config__ = wireframe.new("client")
calendar.__config__ = wireframe.new("calendar")
actor.__config__ = wireframe.new("actor")

# have the server start listening for connections
server.__instance__.start_listening(client.ClientFactory())
