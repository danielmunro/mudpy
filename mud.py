from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from mudpy.client import ClientFactory
from mudpy.heartbeat import Heartbeat
from mudpy.parser.parser import Parser
from mudpy.debug import Debug
from mudpy.stopwatch import Stopwatch

stopwatch = Stopwatch()
heartbeat = Heartbeat(reactor, stopwatch)

Parser.initializeParsers()
Debug.log('scripts initialized')

endpoint = TCP4ServerEndpoint(reactor, 9000)
endpoint.listen(ClientFactory(heartbeat))
reactor.callInThread(heartbeat.start)
Debug.log('mud ready to accept clients ['+str(stopwatch)+'s]')

reactor.run()
Debug.log('mud execution halted')
