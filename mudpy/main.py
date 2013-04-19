from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

import debug, heartbeat, client
from parser import Parser

heartbeat.instance = heartbeat.Heartbeat(reactor)
debug.log('heartbeat initialized')

Parser.startParse('scripts')
debug.log('scripts initialized')

endpoint = TCP4ServerEndpoint(reactor, 9000)
endpoint.listen(client.ClientFactory())
debug.log('mud ready to accept clients')

reactor.callInThread(heartbeat.instance.start)
reactor.run()
debug.log('mud execution halted')
