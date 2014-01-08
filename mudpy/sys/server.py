"""Server interface for game. Mudpy runs in two threads, one with the game loop
and the other with twisted listening in reactor.run(). This module coordinates
communication between the threads.

"""

import random, time, threading, socketserver
from . import wireframe, debug, observer, client

def start(publisher=observer.Observer()):
    """Takes a client_factory (twisted Factory implementation), and set a tcp
    endpoint for the twisted reactor. Set the method for reactor to call in a
    new thread when it starts listening for clients. This method will run the
    main game loop.

    """
    
    server = ThreadedTCPServer(publisher, wireframe.create("config.server"))

    # start the server listening for clients
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    ip, port = server.server_address
    debug.info("listening on "+ip+":"+str(port))

    # main game loop
    server.heartbeat()

def _time():
    return int(time.time())

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Server will create a handler thread for each new client request.
    Handlers are responsible for input buffering from the client, as well as
    setup and shutdown.

    """

    def setup(self):
        """Called when a client connects."""

        _client = client.Client(self)

        debug.info(str(_client)+" connected")
        self.write(self.server.config["messages"]["connection_made"]+" ")

        self.activate_client(_client)
        self.server.clients[self.request] = _client

    def handle(self):
        """Thread that handles adding input to a client's input buffer. The
        main game thread then processes the input buffer as it wants to. The
        input buffer may not automatically get read, such as if the user has
        a delay applied to them.

        """

        data = b""
        _client = self.server.clients[self.request]

        while data != "quit":
            data = _client.read()
            if data:
                _client.input_buffer.append(data)

    def write(self, message):
        self.request.sendall(bytes(message, self.server.config["encoding"]))

    def finish(self):
        """Called when a client disconnects."""
        
        _client = self.server.clients[self.request]
        publisher = self.server.publisher

        debug.info(str(_client)+" disconnected")
        self.write(self.server.config["messages"]["connection_lost"])

        _client.user.get_room().move_actor(_client.user)
        _client.user.save()
        self.deactivate_client(_client)
        _client.user.fire("actor_leaves_realm", _client.user)
        del self.server.clients[self.request]

    def activate_client(self, _client):
        self.server.publisher.on("cycle", _client.stream_input_chunk)

    def deactivate_client(self, _client):
        self.server.publisher.off("cycle", _client.stream_input_chunk)


class ThreadedTCPServer(socketserver.ThreadingTCPServer):
    """Game server, spins off a thread whenever a new client connects and
    updates them when certain game actions happen.

    """

    allow_reuse_address = True

    def __init__(self, publisher, config):
        self.clients = {}
        self.config = config
        self.publisher = publisher

        # pylint thinks socketserver.ThreadingTCPServer is an old-style class
        socketserver.ThreadingTCPServer.__init__(
                self,
                (self.config['host'], self.config['port']),
                ThreadedTCPRequestHandler)

    def heartbeat(self):
        """Main game loop. Fires timed interval events that observers are
        listening for, timekeeper for all game events. Events are described
        below:

            * 'cycle' - will fire once for each completed game loop cycle.
            Listeners on this event should be minimal.

            * 'pulse' - fires in relatively short intervals (1-2 seconds,
            depending on configuration), controls flow of game battles.

            * 'tick' - fires in relatively longer intervals, intended for regen
            of characters, etc.

        """

        pulse_interval = self.config['intervals']['pulse']
        tick_lowbound = self.config['intervals']['tick']['lowbound']
        tick_highbound = self.config['intervals']['tick']['highbound']

        next_pulse = _time() + pulse_interval
        next_tick = _time() + random.randint(tick_lowbound, tick_highbound)

        while True:
            self.publisher.fire('cycle')
            if _time() >= next_pulse:
                next_pulse += pulse_interval
                self.publisher.fire('pulse')
                self.publisher.fire('stat')
            if _time() >= next_tick:
                next_tick = _time() + \
                        random.randint(tick_lowbound, tick_highbound)
                self.publisher.fire('tick')
                rel_next_tick = next_tick - _time()
                debug.info("tick; next in "+str(rel_next_tick)+" seconds")
