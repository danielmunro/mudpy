"""mud.py client classes, hooks in with twisted via the twisted's reactor and
mud.py's ClientFactory. Handles connection, and i/o with the client.

"""

from twisted.internet.protocol import Factory as tFactory, Protocol
from . import debug, observer, actor, wireframe, event
import __main__

__config__ = None

if '__mudpy__' in __main__.__dict__:

    def initialize_client(_event = None):

        global __config__

        __config__ = wireframe.create("config.client")

    __main__.__mudpy__.on('initialize', initialize_client)

class Client(observer.Observer, Protocol):
    """twisted client protocol, defines behavior for clients."""

    def __init__(self):
        self.input_buffer = []
        self.client_factory = None
        self.user = None
        self.observers = {}
        self.login = Login()
        self.events = wireframe.create("event.client")
        self.events.on_events(self)

    def connectionMade(self):
        self.write(__config__.messages["connection_made"])
        debug.log("new client connected")
    
    def connectionLost(self, reason):
        self.write(__config__.messages["connection_lost"])
        debug.log("client disconnected")
    
    def disconnect(self):
        """Called when a client loses their connection."""

        self.client_factory.fire("destroyed", self)
        self.client_factory.clients.remove(self)
        self.user.get_room().move_actor(self.user)
        self.transport.loseConnection()
    
    def dataReceived(self, data):
        self.input_buffer.append(data.strip())

    def poll(self, _event = None):
        """Game cycle listener, will pop off input from the client's command
        buffer and trigger an input event on the client object.

        """

        if self.input_buffer:
            data = self.input_buffer.pop(0)
            if data:
                sender = self.user if self.user else self
                return self.fire("input", sender, data.split(" "))
    
    def write(self, message):
        """Send a message from the game to the client."""

        self.transport.write(str(message)+" ")

    def input_not_handled(self):
        self.write("What was that?")
    
class Login(observer.Observer):
    """Login class, encapsulates relatively procedural login steps."""

    def __init__(self):
        self.todo = ["login", "race", "alignment"]
        self.done = []
        self.newuser = None
        super(Login, self).__init__()
    
    def step(self, _event, client, data):
        """Called for each successive step of the login/alt creation
        process.

        """

        data = " ".join(data)

        def login(data):
            """First step of login process. Check if requested alt exists or
            is a new alt.

            """

            from . import actor

            if not actor.User.is_valid_name(data):
                raise LoginException(__config__.messages["creation_name_not_valid"])

            user = actor.User.load(data)
            if user:
                user.set_client(client)
                client.user = user
                client.fire("loggedin", client)
                return
            self.newuser = actor.User()
            self.newuser.set_client(client)
            self.newuser.name = data
            client.write(__config__.messages["creation_race_query"])

        def race(data):
            """If a new alt, have them select a race."""

            try:
                self.newuser.race = wireframe.create_from_match("race."+data)
            except KeyError:
                raise LoginException(__config__.messages["creation_race_not_valid"])

            client.write(__config__.messages["creation_alignment_query"])
        
        def alignment(data):
            """New alts need an alignment."""

            if "good".find(data) == 0:
                self.newuser.alignment = 1000
            elif "neutral".find(data) == 0:
                self.newuser.alignment = 0
            elif "evil".find(data) == 0:
                self.newuser.alignment = -1000
            else:
                raise LoginException(__config__.messages["creation_alignment_not_valid"])
            client.user = self.newuser
            client.fire("loggedin", client)
            self.newuser.save()
            debug.log("client created new user as "+str(self.newuser))

        step = self.todo.pop(0)

        try:
            locals()[step](data)
            self.done.append(step)
            return True
        except LoginException as error:
            client.write(error)
            self.todo.insert(0, step)

class ClientFactory(tFactory, observer.Observer):
    """twisted factory implementation, used by twisted's reactor to create
    mud.py clients.

    """

    protocol = Client

    def __init__(self):
        self.observers = {}
        self.clients = []
        super(ClientFactory, self).__init__()

    def buildProtocol(self, addr):
        """Called when a new connection is established. Setup method for the
        client object.

        """

        client = Client()
        client.client_factory = self
        self.fire("created", client)
        self.clients.append(client)
        return client

class LoginException(Exception):
    """Raised when unexpected input in received during the login process."""

    pass
