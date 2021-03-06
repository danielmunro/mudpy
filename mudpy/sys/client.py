"""mud.py client classes, hooks in with twisted via the twisted's reactor and
mud.py's ClientFactory. Handles connection, and i/o with the client.

"""

from . import debug, observer, wireframe
from ..game import actor
from ..game.actor import user
import __main__

__config__ = wireframe.create("config.client")

class Client(observer.Observer):
    """twisted client protocol, defines behavior for clients."""

    def __init__(self, ip, request):
        self.ip = ip
        self.input_buffer = []
        self.last_input = ""
        self.user = None
        self.request = request
        super(Client, self).__init__()
        self.login = Login()
        self.on("loggedin", self._loggedin)
        self.on("input", self.login.step)
        self.on("input.__unhandled__", self._input_unhandled)

    def write(self, message):
        self.request.sendall(bytes(message, "UTF-8"))

    def poll(self, _event = None):
        """Game cycle listener, will pop off input from the client's command
        buffer and trigger an input event on the client object.

        """

        if self.input_buffer:
            data = self.input_buffer.pop(0)
            if data:
                sender = self.user if self.user else self
                self.last_input = data if not data == "!" else self.last_input
                return self.fire("input", sender, str(self.last_input).split(" "))

    def _input_unhandled(self, _event = None, _subscriber = None, _arg = None):
        if self.user:
            self.user.notify(__config__["messages"]["input_not_handled"])

    def _loggedin(self, _event, user):
        self.off("input", self.login.step)
        self.on("input", user.input)
        self.user = user
        self.user.client = self
        user.loggedin()

    def __str__(self):
        return self.ip
    
class Login(observer.Observer):
    """Login class, encapsulates relatively procedural login steps."""

    def __init__(self):
        self.todo = ["login", "race", "alignment"]
        self.done = []
        self.newuser = None
        super(Login, self).__init__()
    
    def step(self, event, client, data):
        """Called for each successive step of the login/alt creation
        process.

        """

        data = " ".join(data)

        def login(data):
            """First step of login process. Check if requested alt exists or
            is a new alt.

            """

            if not actor.user.is_valid_name(data):
                raise LoginException(__config__["messages"]["creation_name_not_valid"])

            user = actor.user.load(data)
            if user:
                #user.client = client
                client.fire("loggedin", user)
                return
            self.newuser = actor.user.User()
            #self.newuser.client = client
            self.newuser.name = data
            client.write(__config__["messages"]["creation_race_query"]+" ")

        def race(data):
            """If a new alt, have them select a race."""

            try:
                self.newuser.race = wireframe.create_from_match("race."+data)
            except KeyError:
                raise LoginException(__config__["messages"]["creation_race_not_valid"])

            client.write(__config__["messages"]["creation_alignment_query"]+" ")
        
        def alignment(data):
            """New alts need an alignment."""

            if "good".find(data) == 0:
                self.newuser.alignment = 1000
            elif "neutral".find(data) == 0:
                self.newuser.alignment = 0
            elif "evil".find(data) == 0:
                self.newuser.alignment = -1000
            else:
                raise LoginException(__config__["messages"]["creation_alignment_not_valid"])
            client.fire("loggedin", self.newuser)
            self.newuser.save()
            debug.log("client created new user as "+str(self.newuser))

        step = self.todo.pop(0)

        try:
            locals()[step](data)
            self.done.append(step)
            event.handle()
        except LoginException as error:
            client.write(error)
            self.todo.insert(0, step)

class LoginException(Exception):
    """Raised when unexpected input in received during the login process."""

    pass
