"""Server interface for game. Mudpy runs in two threads, one with the game loop
and the other with twisted listening in reactor.run(). This module coordinates
communication between the threads.

"""

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import random, time, __main__
from . import wireframe, debug, observer

__config__ = wireframe.create("config.server")
__init_time__ = time.time()

if '__mudpy__' in __main__:
    __publisher__ = getattr(__main__, '__mudpy__')
else:
    __publisher__ = observer.Observer()

def heartbeat():
    """Callback provided to twisted for communicating between game threads."""

    next_pulse = time.time()+__config__['intervals']['pulse']
    next_tick = time.time()+random.randint(
        __config__['intervals']['tick']['lowbound'], \
        __config__['intervals']['tick']['highbound'])
    while(1):
        __publisher__.fire('cycle')
        if time.time() >= next_pulse:
            next_pulse += __config__['intervals']['pulse']
            __publisher__.fire('pulse')
            __publisher__.fire('stat')
        if time.time() >= next_tick:
            next_tick = int(time.time()+random.randint(
                __config__['intervals']['tick']['lowbound'], \
                __config__['intervals']['tick']['highbound']))
            __publisher__.fire('tick')
            rel_next_tick = int(next_tick-time.time())
            debug.log("tick; next in "+str(rel_next_tick)+" seconds")

def start(client_factory):
    """Takes a client_factory (twisted Factory implementation), and set a tcp 
    endpoint for the twisted reactor. Set the method for reactor to call in a
    new thread when it starts listening for clients. This method will run the 
    main game loop.

    """

    debug.log("listening on port "+str(__config__['port']))

    # define an endpoint for the reactor in mud.py's ClientFactory, an
    # implementation of twisted's Factory
    TCP4ServerEndpoint(reactor, __config__['port']).listen(client_factory)

    # start running the game thread
    reactor.callInThread(heartbeat)

    # start the twisted client listener thread
    reactor.run()
