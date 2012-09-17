from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from client import ClientFactory
from heartbeat import Heartbeat
from parser import Parser

heartbeat = Heartbeat(reactor)
Parser("areas")

endpoint = TCP4ServerEndpoint(reactor, 9000)
endpoint.listen(ClientFactory(heartbeat))

reactor.callInThread(heartbeat.start)
reactor.run()
