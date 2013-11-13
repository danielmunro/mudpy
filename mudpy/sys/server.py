"""Server interface for game. Mudpy runs in two threads, one with the game loop
and the other with twisted listening in reactor.run(). This module coordinates
communication between the threads.

"""

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import random, time
from . import observer, wireframe

__config__ = wireframe.create("config.server")

class Instance(observer.Observer):
    """Runs the twisted reactor and provides a callback for the main game
    thread.

    """
    
    def __init__(self, mudpy):
        self.mudpy = mudpy
        self.starttime = time.time()
        super(Instance, self).__init__()

    def start(self, client_factory):
        """Takes a client_factory (twisted Factory implementation), and set it
        for a tcp endpoint for the twisted reactor. Set the method for reactor
        to call in a new thread when it starts listening for clients. This 
        method will start the main game loop.

        """

        # call set_client_poll whenever client_factory creates a new client,
        # and call unset_client_poll when clients are destroyed
        client_factory.on("created", self._set_client_poll)
        client_factory.on("destroyed", self._unset_client_poll) 

        # define an endpoint for the reactor in mud.py's ClientFactory, an
        # implementation of twisted's Factory
        TCP4ServerEndpoint(reactor, __config__.port).listen(client_factory)

        # start running the game thread
        reactor.callInThread(self._heartbeat)

        # start the twisted client listener thread
        reactor.run()

    def _heartbeat(self):
        """Callback provided to twisted for communicating between game threads.

        """

        next_pulse = time.time()+__config__.intervals['pulse']
        next_tick = time.time()+random.randint(
            __config__.intervals['tick']['lowbound'], \
            __config__.intervals['tick']['highbound'])
        while(1):
            self.mudpy.fire('cycle')
            if time.time() >= next_pulse:
                next_pulse += __config__.intervals['pulse']
                self.mudpy.fire('pulse')
                self.mudpy.fire('stat')
            if time.time() >= next_tick:
                next_tick = time.time()+random.randint(
                    __config__.intervals['tick']['lowbound'], \
                    __config__.intervals['tick']['highbound'])
                self.mudpy.fire('tick')

    def _set_client_poll(self, _event, client):
        """Called when the client_factory reports that a client is created.
        Sets a polling listener on the newly created client for each game
        cycle.
        
        """

        self.mudpy.on("cycle", client.poll)

    def _unset_client_poll(self, _event, client):
        """Called when the client_factory reports that a client has been
        destroyed. Removes the polling listener for that client.

        """

        self.mudpy.off("cycle", client.poll)
    
    def __str__(self):
        return str(__config__)
