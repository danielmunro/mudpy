"""A server instance class, essentially a container class for config loaded
user defined scripts.

"""
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import random, time
from . import client, debug, observer

class Instance:
    """Information about the implementation of this mud.py server."""
    
    def __init__(self):

        # reference for a server Instance config. factory will use it as a 
        # a unique identifier
        self.name = ""

        # the port to listen on for connections from telnet clients
        self.port = 0

        # display_name is the name of the particular mud being built using
        # mud.py framework.
        self.display_name = ""

        # initialize heartbeat, which records the time of initialization and keeps
        # track of its own reference to the reactor. Heartbeat uses reactor to call
        # functions in the game thread from the thread listening to the network
        self.heartbeat = Heartbeat()

    def start_listening(self):
        """Create a server end point with a twisted reactor and a port, then
        tell it to use mud.py's client.ClientFactory to create clients on
        connection.

        """

        TCP4ServerEndpoint(reactor, self.port).listen(client.ClientFactory())
        debug.log(str(self)+" ready to accept clients on port "+str(self.port))

        # start running the game thread
        reactor.callInThread(self.heartbeat.start)

        # start the twisted client listener thread
        reactor.run()
    
    def __str__(self):
        return self.name

class Heartbeat(observer.Observer):
    """The timekeeper for mud.py. Fires off game cycles for each loop within
    the main game loop, as well as pulses every second, and ticks in random
    higher intervals. Each of these events are used by different objects in
    the game to keep internal time for various tasks.

    """

    TICK_LOWBOUND_SECONDS = 10
    TICK_HIGHBOUND_SECONDS = 15

    PULSE_SECONDS = 1

    def __init__(self):
        self.stopwatch = Stopwatch()
        super(Heartbeat, self).__init__()
        debug.log('heartbeat created')
    
    def start(self):
        """Start the server heartbeat, which will consume this thread with the
        main game loop.

        """

        debug.log('heartbeat initialized')
        next_pulse = time.time()+Heartbeat.PULSE_SECONDS
        next_tick = time.time()+random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, \
                                                Heartbeat.TICK_HIGHBOUND_SECONDS)
        while(1):
            self.dispatch('cycle')
            if time.time() >= next_pulse:
                next_pulse += Heartbeat.PULSE_SECONDS
                self.dispatch('pulse', 'stat')
            if time.time() >= next_tick:
                next_tick = time.time()+random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, \
                                                        Heartbeat.TICK_HIGHBOUND_SECONDS)
                _stop = Stopwatch()
                self.dispatch('tick')
                debug.log('dispatched tick ['+str(_stop)+'s elapsed in tick] ['+ \
                                    str(self.stopwatch)+'s elapsed since start]')

    def dispatch(self, *eventlist, **events):
        """Custom dispatch method for the heartbeat. Instead of calling the
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
                [reactor.callFromThread(func, args) for func in self.observers[event]]
            except KeyError:
                pass

class Stopwatch:
    def __init__(self):
        self.starttime = time.time()
    
    def __str__(self):
        return str(time.time()-self.starttime)

__instance__ = Instance()
