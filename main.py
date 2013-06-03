"""Entry point for mud.py. Creates a server instance, parses config based on
arguments from the cli, assigns a configuration to the server and starts
listening on the configured port.

"""

from mudpy import observer

class Mudpy(observer.Observer):
    """Anchor object for attaching initialization functions to. Dispatches
    an initialization event after all script parsing is complete.

    """

    def __init__(self):
        super(Mudpy, self).__init__()

__mudpy__ = Mudpy()

from mudpy import factory, server, client, debug

__mudpy__.dispatch("preload")

import sys, os

# set the data directory for storing users and calendar time

if not os.path.isdir("data"):
    try:
        os.mkdir("data")
    except IOError:
        debug.log("create a writable \"data\" directory for mudpy to use",
                "error")
        raise

# set some global variables from arguments passed to the script

try:
    __python_path__ = sys.argv[1]
    __mud_name__ = sys.argv[2]
    __scripts_directory__ = os.path.join(__python_path__, "scripts")
except IndexError:
    debug.log("invalid set of arguments passed to mud.py. expecting two "+ \
                "arguments: the location of the scripts directory and the "+ \
                "name of the mud instance to initialize (from the scripts "+ \
                "base init.json configuration, ie:\n\n python main.py "+ \
                "mudpy/scripts mud\n", "error")
    raise

# set the path for the mud that is being run

sys.path.append(os.path.join(os.getcwd(), __python_path__))

# parse the scripts directories, sets up all of the initial state for the game,
# as well as wireframes for building more game objects during the run

try:
    factory.parse("mudpy/scripts")
except IOError:
    debug.log("internal mudpy scripts directory appears to be missing",
            "error")
    raise

try:
    factory.parse(__scripts_directory__)
except IOError:
    debug.log("invalid scripts directory passed in as first argument. This "+ \
                "is the location of the scripts that define game objects for"+ \
                "mud.py", "error")
    raise

# run initialization
__mudpy__.dispatch("initialize")

# start listening
server.__instance__.start_listening(client.ClientFactory())
