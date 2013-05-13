"""Entry point for mud.py. Creates a server instance, parses config based on
arguments from the cli, assigns a configuration to the server and starts
listening on the configured port.

"""

from mudpy import factory, server, client, debug
import sys

# set some global variables from arguments passed to the script

try:
    __scripts_directory__ = sys.argv[1]
    __mud__name__ = sys.argv[2]
except IndexError:
    debug.log("invalid set of arguments passed to mud.py. expecting two "+ \
                "arguments: the location of the scripts directory and the "+ \
                "name of the mud instance to initialize (from the scripts "+ \
                "base init.json configuration, ie:\n\n python main.py "+ \
                "mudpy/scripts mud\n", "error")

# parse the scripts directories, sets up all of the initial state for the game,
# as well as wireframes for building more game objects during the run

factory.parse('mudpy/scripts')

try:
    factory.parse(__scripts_directory__)
except IOError:
    debug.log("invalid scripts directory passed in as first argument. This "+ \
                "is the location of the scripts that define game objects for"+ \
                "mud.py", "error")

# assign a configuration to the server instance, parsed from the
# __scripts_directory__. Start the configured server, and have it use the
# ClientFactory to handle new connections

try:
    factory.new(server.__instance__, __mud__name__).start_listening(\
                                                    client.ClientFactory())
except factory.FactoryException:
    debug.log("invalid mud name passed as second argument. This needs to be"+ \
                "the Instance name defined in your scripts/init.json", "error")
