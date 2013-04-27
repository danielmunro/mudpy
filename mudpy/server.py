"""A server instance class, essentially a container class for config loaded
user defined scripts.

"""
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from . import heartbeat, client, debug

# initialize heartbeat, which records when the instance was started and keeps
# track of its own reference to the reactor. Heartbeat uses reactor to call
# functions in the game thread from the thread listening to the network
heartbeat.instance = heartbeat.Heartbeat(reactor)

class Instance:
	"""Information about the implementation of this mud.py server."""
	
	def __init__(self):

		# reference for a server Instance config. factory will use it as a 
		# a unique identifier
		self.name = ""

		# the port to listen on for connections from telnet clients
		self.port = 0

		# display_name is the name of the particular mud being built using
		# mud.py framework.
		self.display_name = ""

	def start_listening(self):
		"""Create a server end point with a twisted reactor and a port, then
		tell it to use mud.py's client.ClientFactory to create clients on
		connection.

		"""

		TCP4ServerEndpoint(reactor, self.port).listen(client.ClientFactory())
		debug.log(str(self)+" ready to accept clients on port "+str(self.port))

		# start running the game thread
		reactor.callInThread(heartbeat.instance.start)

		# start the twisted client listener thread
		reactor.run()
	
	def __str__(self):
		return self.name
