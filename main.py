"""Entry point for mud.py. Creates a server instance, parses config based on
arguments from the cli, assigns a configuration to the server and starts
listening on the configured port.

"""

from mudpy import factory, server, debug
import sys

# set some global variables from arguments passed to the script
__scripts_directory__ = sys.argv[1]
__mud__name__ = sys.argv[2]

# create a generic server instance, initializes a heartbeat
__server_instance__ = server.Instance()

# parse the scripts directory, sets up all of the initial state for the game,
# as well as wireframes for building more game objects during the run
try:
	factory.parse(__scripts_directory__)
except IOError:
	debug.log("invalid scripts directory passed in as first argument. This "+ \
				"is the location of the scripts that define game objects for"+ \
				"mud.py", "error")

# assign a configuration to the server instance, parsed from the
# __scripts_directory__, and start running it.
try:
	factory.new(__server_instance__, __mud__name__).start_listening()
except factory.FactoryException:
	debug.log("invalid mud name passed as second argument. This needs to be"+ \
				"the Instance name defined in your scripts/init.json", "error")
