"""Entry point for mud.py. Set the scripts path from args, which is used to
load areas, wireframes, and game data. Instantiate the server, calendar,
and wireframes.

"""

from mudpy import wireframe, debug
import sys

try:
    wireframe.path = sys.argv[1]
    wireframe.preload()
except IndexError:
    debug.log("need to specify an initialization path", "error")
    raise

from mudpy import server, calendar, room, actor, client
server.__instance__ = server.Instance()
calendar.load(server)

try:
    wireframe.execute()
except IOError:
    debug.log("specified path does not exist: "+wireframe.path, "error")
    raise

server.__instance__.start_listening(client.ClientFactory())
