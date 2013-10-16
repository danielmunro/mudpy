"""Entry point for mud.py. Set the scripts path from args, which is used to
load areas, wireframes, and game data. Instantiate the server, calendar,
and wireframes.

Wireframes need to be set up in order to import game modules (server, calendar,
and client).

"""

from mudpy import wireframe, debug
import sys

try:
    wireframe.load_wireframes(sys.argv[1])
except IndexError:
    debug.log("need to pass in a path, ie python mud.py example", "error")
    raise
except IOError:
    debug.log("path does not exist: "+sys.argv[1], "error")
    raise

from mudpy import server, calendar, client

try:
    calendar.__instance__ = wireframe.create("calendar", "data")
except wireframe.WireframeException:
    calendar.__instance__ = calendar.Instance()

server.__instance__ = server.Instance()
server.__instance__.heartbeat.attach("tick", calendar.__instance__.tick)
wireframe.load_areas()
server.__instance__.start_listening(client.ClientFactory())
