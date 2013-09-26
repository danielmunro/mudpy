"""Entry point for mud.py. Creates a server instance, parses config based on
arguments from the cli, assigns a configuration to the server and starts
listening on the configured port.

"""

from mudpy import factory, server, debug, client, calendar, actor
import sys, os

try:
    __python_path__ = sys.argv[1]
    __mud_name__ = sys.argv[2]
except IndexError:
    debug.log("invalid set of arguments passed to mud.py. expecting two "+ \
                "arguments: the location of the scripts directory and the "+ \
                "name of the mud instance to initialize (from the scripts "+ \
                "base init.json configuration, ie:\n\n python main.py "+ \
                "mudpy/scripts mud\n", "error")
    raise

# data directory is for storing users and in-game time
try:
    os.mkdir("data")
except IOError: # permissions error creating dir
    debug.log("create a writable \"data\" directory for mudpy to use",
            "error")
    raise
except OSError: # already exists
    pass

# set the path for the mud that is being run
sys.path.append(os.path.join(os.getcwd(), __python_path__))

# server instance -- needed by dependencies in factory
server.__instance__ = server.Instance()

# load in-game calendar details
calendar.load_calendar()

# parse the scripts directory, sets up all of the initial state for the game,
# as well as wireframes for building more game objects during the run
__scripts_directory__ = os.path.join(__python_path__, "scripts")

try:
    factory.parse(__scripts_directory__)
except IOError:
    debug.log("invalid scripts directory passed in as first argument. This "+ \
                "is the location of the scripts that define game objects for"+ \
                "mud.py", "error")
    raise

# configuration values
calendar.__config__ = factory.new(calendar.Config(), __mud_name__)
actor.__config__ = factory.new(actor.Config(), __mud_name__)
client.__config__ = factory.new(client.Config(), __mud_name__)
server.__config__ = factory.new(server.Config(), __mud_name__)

# have the server start listening for connections
server.__instance__.start_listening(client.ClientFactory())
