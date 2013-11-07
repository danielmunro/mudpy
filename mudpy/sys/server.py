from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import random, time
from . import debug, observer, wireframe, config

__config__ = wireframe.create("config.server")

class Instance(observer.Observer):
    
    def __init__(self, mudpy):
        # initialize heartbeat, which records the time of initialization and
        # keeps track of its own reference to the reactor. Heartbeat uses
        # reactor to call functions in the game thread from the thread
        # listening to the network
        self.heartbeat = Heartbeat(mudpy)
        self.mudpy = mudpy
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
        reactor.callInThread(self.heartbeat.start)

        debug.log(str(self)+" ready to accept clients on port "+str(__config__.port))

        # start the twisted client listener thread
        reactor.run()

    def _set_client_poll(self, _event, client):
        """Called when the client_factory reports that a client is created."""

        self.mudpy.on("cycle", client.poll)

    def _unset_client_poll(self, _event, client):
        """Called when the client_factory reports that a client has been
        destroyed.

        """

        self.mudpy.off("cycle", client.poll)
    
    def __str__(self):
        return str(__config__)

class Heartbeat(observer.Observer):
    """The timekeeper for mud.py. Fires off game cycles for each loop within
    the main game loop, as well as pulses every second, and ticks in random
    higher intervals. Each of these events are used by different objects in
    the game to keep internal time for various tasks.

    """

    TICK_LOWBOUND_SECONDS = 10
    TICK_HIGHBOUND_SECONDS = 15

    PULSE_SECONDS = 1

    def __init__(self, mudpy):
        self.mudpy = mudpy
        self.observers = {}
        self.stopwatch = Stopwatch()
        super(Heartbeat, self).__init__()
        debug.log('heartbeat created')
    
    def start(self):
        """Start the server heartbeat, which will consume this thread with the
        main game loop.

        """

        debug.log('heartbeat initialized')
        next_pulse = time.time()+Heartbeat.PULSE_SECONDS
        next_tick = time.time()+random.randint(
                                        Heartbeat.TICK_LOWBOUND_SECONDS, \
                                        Heartbeat.TICK_HIGHBOUND_SECONDS)
        while(1):
            self.mudpy.fire('cycle')
            if time.time() >= next_pulse:
                next_pulse += Heartbeat.PULSE_SECONDS
                self.mudpy.fire('pulse')
                self.mudpy.fire('stat')
            if time.time() >= next_tick:
                next_tick = time.time()+random.randint(
                                        Heartbeat.TICK_LOWBOUND_SECONDS, \
                                        Heartbeat.TICK_HIGHBOUND_SECONDS)
                _stop = Stopwatch()
                self.mudpy.fire('tick')
                debug.log('fireed tick ['+str(_stop)+'s elapsed in tick]'+ \
                            ' ['+str(self.stopwatch)+'s elapsed since start]')

    def fire(self, *eventlist, **events):
        """Custom fire method for the heartbeat. Instead of calling the
        functions directly, we need to tell the twisted reactor to call them
        in the main thread.

        """

        for event in eventlist:
            try:
                [reactor.callFromThread(func) for func in self.observers[event]]
            except KeyError:
                pass

        for event, args in events.iteritems():
            try:
                [reactor.callFromThread(func, args) for func in \
                                            self.observers[event]]
            except KeyError:
                pass

class Stopwatch:
    """Timekeeper, used for debugging mostly."""

    def __init__(self):
        self.starttime = time.time()
    
    def __str__(self):
        return str(time.time()-self.starttime)
