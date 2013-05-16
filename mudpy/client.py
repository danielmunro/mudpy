"""mud.py client classes, hooks in with twisted via the twisted's reactor and
mud.py's ClientFactory. Handles connection, and i/o with the client.

"""

from twisted.internet.protocol import Factory as tFactory, Protocol
from . import debug, factory, observer

class Client(observer.Observer, Protocol):
    """twisted client protocol, defines behavior for clients."""

    def __init__(self):
        self.commandbuffer = []
        self.client_factory = None
        self.user = None
        self.login = Login(self)
        super(Client, self).__init__()

    def connectionMade(self):
        self.write("By what name do you wish to be known? ")
        debug.log('new client connected')
    
    def connectionLost(self, reason):
        self.write("Good bye!")
        debug.log('client disconnected')
    
    def disconnect(self):
        """Called when a client loses their connection."""

        self.client_factory.dispatch('destroyed', client=self)
        self.user.room.actors.remove(self.user)
        self.transport.loseConnection()
    
    def dataReceived(self, data):
        self.commandbuffer.append(data.strip())

    def get_new_user(self):
        """Returns a user of the type defined in the configs."""

        user_module = __import__(self.client_factory.config.user_module, None, None, 'User')
        return user_module.User()
    
    def poll(self):
        """Listener for game cycle, checks the command buffer for new input.
        If a user is logged in dispatch an input event, which will notify
        command, ability, and other listeners. Otherwise, attempt to continue
        the login process.

        """

        try:
            data = self.commandbuffer.pop(0)
        except IndexError:
            return
    
        if not self.user:
            return self.login.step(data)
        elif data:
            args = data.split(" ")
            handled = self.dispatch('input', user=self.user, args=args)
            if not handled:
                self.user.notify("What was that?")

        self.write("\n"+self.user.prompt())
    
    def write(self, message):
        """Send a message from the game to the client."""

        self.transport.write(str(message))
    
class Login:
    """Login class, encapsulates relatively procedural login steps."""

    def __init__(self, client):
        self.todo = ['login', 'race', 'alignment']
        self.done = []
        self.client = client
        self.newuser = None
    
    def step(self, data):
        """Called for each successive step of the login/alt creation
        process.

        """

        def login(data):
            """First step of login process. Check if requested alt exists or
            is a new alt.

            """

            from . import actor

            if not actor.is_valid_name(data):
                raise LoginException("That name does not appear to be valid, "+\
                                     "try again. ")

            user = actor.load(data)
            if user:
                user.client = self.client
                self.client.user = user
                user.loggedin()
                return
            self.newuser = self.client.get_new_user()
            self.newuser.client = self.client
            self.newuser.name = data
            self.client.write("What is your race? ")

        def race(data):
            """If a new alt, have them select a race."""

            from . import actor

            try:
                self.newuser.race = factory.new(actor.Race(), data)
            except factory.FactoryException:
                raise LoginException("That is not a valid race. What is "+ \
                                     "your race? ")
            self.client.write("What alignment are you (good/neutral/evil)? ")
        
        def alignment(data):
            """New alts need an alignment."""

            if "good".find(data) == 0:
                self.newuser.alignment = 1000
            elif "neutral".find(data) == 0:
                self.newuser.alignment = 0
            elif "evil".find(data) == 0:
                self.newuser.alignment = -1000
            else:
                raise LoginException("That is not a valid alignment. What "+ \
                                     "is your alignment? ")
            self.client.user = self.newuser
            self.newuser.loggedin()
            self.newuser.save()
            debug.log('client created new user as '+str(self.newuser))

        step = self.todo.pop(0)

        try:
            locals()[step](data)
            self.done.append(step)
        except LoginException as error:
            self.client.write(error)
            self.todo.insert(0, step)

class ClientFactory(tFactory, observer.Observer):
    """twisted factory implementation, used by twisted's reactor to create
    mud.py clients.

    """

    protocol = Client

    def __init__(self):
        self.config = factory.new(Config(), "main")
        super(ClientFactory, self).__init__()

    def buildProtocol(self, addr):
        """Called when a new connection is established. Setup method for the
        client object.

        """

        client = Client()
        client.client_factory = self
        self.dispatch('created', client=client)
        return client

class Config:
    """Maintains configurations specific to the mud mudpy is running."""

    def __init__(self):
        self.user_module = None

class LoginException(Exception):
    """Raised when unexpected input in received during the login process."""

    pass
