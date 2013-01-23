from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from mudpy.client import ClientFactory
from mudpy.heartbeat import Heartbeat

from mudpy.parser.parser import Parser

heartbeat = Heartbeat(reactor)
Parser.initializeParsers()

endpoint = TCP4ServerEndpoint(reactor, 9000)
endpoint.listen(ClientFactory(heartbeat))

reactor.callInThread(heartbeat.start)
reactor.run()
