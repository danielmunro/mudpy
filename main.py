"""Entry point for mud.py. Does a few setup tasks.

1. Starts the heartbeat, which times events like game cycles, pulses (battle
rounds), and ticks.

2. Parses initialization scripts (.json files found in scripts/), which define
everything about this particular game instance, including attributes,
abilities, proficiencies, races, and the world.

3. Starts up the server, which currently has a hardwired configuration to
listen on port 9000.

"""

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from mudpy import debug, heartbeat, client, factory

# initialize heartbeat, which records when the instance was started and keeps
# track of its own reference to the reactor. Heartbeat uses reactor to call
# functions in the game thread from the thread listening to the network
heartbeat.instance = heartbeat.Heartbeat(reactor)
debug.log('heartbeat initialized')

# sets up all of the initial state for the game, as well as wireframes for
# building more game objects during the run
factory.parse('mudpy/scripts')
debug.log('scripts initialized')

# start listening for clients
TCP4ServerEndpoint(reactor, 9000).listen(client.ClientFactory())
debug.log('mud ready to accept clients')

# start running the game thread
reactor.callInThread(heartbeat.instance.start)

# start the twisted client listener thread
reactor.run()

# game is designed to be long running -- this shouldn't really be hit
debug.log('mud execution halted')
