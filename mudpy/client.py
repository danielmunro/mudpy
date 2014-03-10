"""Mudpy client classes, handles connection and i/o with the client."""

from . import observer, mud
from .wireframes import user

class Client(observer.Observer):
    """Represents a telnet connection."""

    def __init__(self, ip, request):
        self.ip = ip
        self.input_buffer = []
        self.last_input = ""
        self.request = request
        self.login = Login()
        self.server = None
        
        super(Client, self).__init__()

    def write(self, message):
        self.request.sendall(bytes(message, "UTF-8"))

    def poll(self, _event = None):
        """Game cycle listener, will pop off input from the client's command
        buffer and trigger an input event on the client object.

        """

        if self.input_buffer:
            self._fire_on_input(self.input_buffer.pop(0))

    def _setup_events(self):

        def _loggedin(_event, user):
            
            self.off("input", self.login.step)
            user.set_client(self)

            user.look()

            def _unhandled_input(*args):
                self.write("Eh?")

            self.on("input", _unhandled_input)
        
        self.on("loggedin", _loggedin)
        self.on("input", self.login.step)

    def _fire_on_input(self, input = ""):
        if input:
            self.last_input = input if not input == "!" else self.last_input
            return self.fire("input", self, str(self.last_input).split(" "))

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

            if not user.is_valid_name(data):
                raise LoginException("That name is not valid. What is your name? ")

            loaded_user = user.load(data)
            if loaded_user:
                client.fire("loggedin", loaded_user)
                return

            self.newuser = user.User(client.server.publisher)
            self.newuser.name = data
            client.write("New user. Choose a race. ")

        def race(data):
            """If a new alt, have them select a race."""

            try:
                self.newuser.set_race(mud.safe_load("races", data))
            except ValueError:
                raise LoginException("That's not a valid race. Choose a race. ")

            client.write("Are you good, neutral, or evil [g/n/e]? ")
        
        def alignment(data):
            """New alts need an alignment."""

            if "good".find(data) == 0:
                self.newuser.alignment = 1000
            elif "neutral".find(data) == 0:
                self.newuser.alignment = 0
            elif "evil".find(data) == 0:
                self.newuser.alignment = -1000
            else:
                raise LoginException("That's not a valid alignment. Are you good, neutral, or evil? ")
            client.fire("loggedin", self.newuser)

        step = self.todo.pop(0)

        try:
            locals()[step](data)
            self.done.append(step)
            event.handle()
        except LoginException as error:
            client.write(str(error))
            self.todo.insert(0, step)

class LoginException(Exception):
    """Raised when unexpected input in received during the login process."""

    pass