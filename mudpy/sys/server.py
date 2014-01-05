"""Server interface for game. Mudpy runs in two threads, one with the game loop
and the other with twisted listening in reactor.run(). This module coordinates
communication between the threads.

"""

import random, time, threading, socketserver
from . import wireframe, debug, observer, client

__config__ = wireframe.create("config.server")
__init_time__ = time.time()

def start(publisher=None):
    """Takes a client_factory (twisted Factory implementation), and set a tcp
    endpoint for the twisted reactor. Set the method for reactor to call in a
    new thread when it starts listening for clients. This method will run the
    main game loop.

    """

    if not publisher:
        publisher = observer.Observer()

    server = ThreadedTCPServer(
            publisher,
            (__config__['host'], __config__['port']),
            ThreadedTCPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    ip, port = server.server_address
    debug.info("listening on "+ip+":"+str(port))
    server.heartbeat()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Server will create a handler thread for each new client request.
    Handlers are responsible for input buffering from the client, as well as
    setup and shutdown.

    """

    def setup(self):
        """Called when a client connects."""

        cl = client.Client(self.request)
        self.server.publisher.on("cycle", cl.poll)
        self.request.sendall(
                bytes(__config__["messages"]["connection_made"]+" ", "UTF-8"))
        self.server.clients[self.request] = cl

    def handle(self):
        """Thread that handles adding input to a client's input buffer. The
        main game thread then processes the input buffer as it wants to. The
        input buffer may not automatically get read, such as if the user has
        a delay applied to them.

        """

        data = b""
        while data != b"quit":
            data = self.request.recv(1024).strip()
            _client = self.server.clients[self.request]
            _client.input_buffer.append(data.decode("UTF-8"))

    def finish(self):
        """Called when a client disconnects."""

        publisher = self.server.publisher
        _client = self.server.clients[self.request]
        message = bytes(__config__["messages"]["connection_lost"], "UTF-8")

        publisher.off("cycle", _client.poll)
        self.request.sendall(message)
        _client.user.get_room().move_actor(_client.user)
        publisher.fire("actor_leaves_realm", _client.user)
        del self.server.clients[self.request]

class ThreadedTCPServer(socketserver.ThreadingTCPServer):
    """Game server, spins off a thread whenever a new client connects and
    updates them when certain game actions happen.

    """

    allow_reuse_address = True

    def __init__(self, publisher, *args):
        self.clients = {}
        self.publisher = publisher

        # pylint thinks socketserver.ThreadingTCPServer is an old-style class
        socketserver.ThreadingTCPServer.__init__(self, *args)

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

        next_pulse = time.time()+__config__['intervals']['pulse']
        next_tick = time.time()+random.randint(
            __config__['intervals']['tick']['lowbound'], \
            __config__['intervals']['tick']['highbound'])
        while True:
            self.publisher.fire('cycle')
            if time.time() >= next_pulse:
                next_pulse += __config__['intervals']['pulse']
                self.publisher.fire('pulse')
                self.publisher.fire('stat')
            if time.time() >= next_tick:
                next_tick = int(time.time()+random.randint(
                    __config__['intervals']['tick']['lowbound'], \
                    __config__['intervals']['tick']['highbound']))
                self.publisher.fire('tick')
                rel_next_tick = int(next_tick-time.time())
                debug.info("tick; next in "+str(rel_next_tick)+" seconds")
