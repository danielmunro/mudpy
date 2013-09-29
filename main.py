"""Entry point for mud.py. Creates a server instance, parses config based on
arguments from the cli, assigns a configuration to the server and starts
listening on the configured port.

"""

from mudpy import server, debug, client, calendar, actor, wireframe
import sys, os

try:
    __python_path__ = sys.argv[1]
    __wireframe_path__ = __python_path__
except IndexError:
    __python_path__ = "data"
    __wireframe_path__ = os.path.join(__python_path__, "wireframes.yaml")

# data directory is for storing users and in-game time
__data__ = "data"
try:
    os.mkdir(__data__)
except IOError: # permissions error creating dir
    debug.log("create a writable \"data\" directory for mudpy to use",
            "error")
    raise
except OSError: # already exists
    pass

# set the path for the mud that is being run
sys.path.append(os.path.join(os.getcwd(), __python_path__))

# parse the scripts directory, sets up all of the initial state for the game,
# as well as wireframes for building more game objects during the run

try:
    wireframe.load(__wireframe_path__)
except IOError:
    debug.log("invalid scripts directory passed in as first argument. This "+ \
                "is the location of the scripts that define game objects for"+ \
                "mud.py", "error")
    raise

# setup admin command for this
#wireframe.save(__data__)

server.__instance__ = server.Instance()

# load in-game calendar details
calendar.load_calendar()

# configuration values
server.__config__ = wireframe.new("server")
client.__config__ = wireframe.new("client")
calendar.__config__ = wireframe.new("calendar")
actor.__config__ = wireframe.new("actor")

# have the server start listening for connections
server.__instance__.start_listening(client.ClientFactory())
