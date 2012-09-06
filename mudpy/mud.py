from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from client import ClientFactory
from heartbeat import Heartbeat
from parser import Parser

Parser("areas")

heartbeat = Heartbeat()

# 8007 is the port you want to run under. Choose something >1024
endpoint = TCP4ServerEndpoint(reactor, 9000)
endpoint.listen(ClientFactory(heartbeat))
reactor.callInThread(heartbeat.start)
reactor.run()
