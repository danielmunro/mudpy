from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from mudpy.client import ClientFactory
from mudpy.heartbeat import Heartbeat
from mudpy.debug import Debug
from mudpy.parser import Parser

heartbeat = Heartbeat(reactor)

Parser.startParse('scripts')
Debug.log('scripts initialized')

endpoint = TCP4ServerEndpoint(reactor, 9000)
endpoint.listen(ClientFactory())
reactor.callInThread(heartbeat.start)
Debug.log('mud ready to accept clients')

reactor.run()
Debug.log('mud execution halted')
