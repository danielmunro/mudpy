from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

import debug
from client import ClientFactory
from heartbeat import Heartbeat
from parser import Parser

heartbeat = Heartbeat(reactor)

Parser.startParse('scripts')
debug.log('scripts initialized')

endpoint = TCP4ServerEndpoint(reactor, 9000)
endpoint.listen(ClientFactory())
reactor.callInThread(heartbeat.start)
debug.log('mud ready to accept clients')

reactor.run()
debug.log('mud execution halted')
