from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from client import ClientFactory
from heartbeat import Heartbeat
from parser.area import AreaParser

heartbeat = Heartbeat(reactor)
AreaParser().initializeRooms()

endpoint = TCP4ServerEndpoint(reactor, 9000)
endpoint.listen(ClientFactory(heartbeat))

reactor.callInThread(heartbeat.start)
reactor.run()
