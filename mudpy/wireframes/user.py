from .. import actor, mud

def load(name):
    mud.safe_load("users", name)

def is_valid_name(name):
    name_len = len(name)
    return name.isalpha() and name_len > 2 and name_len < 12

class User(actor.Actor):

    yaml_tag = "user"

    def __init__(self):

        self.client = None

        super(User, self).__init__()

    def set_client(self, client):
        
        self.client = client

        def _input(event, client, args):
        
            command_name = args[0]
            command_args = args[1:]

            command = mud.safe_load("commands", command_name)

            if command:
                command.run(self, command_args)
                event.handle()
        
        self.client.on("input", _input)
        self.client.on("input.__done__", self._prompt)

    def notify(self, message):
        self.client.write(message)

    def test(self):
        self.notify("This is a test of the public broadcast system.")

    def _prompt(self, *_args):
        self.client.write(("\n\n%ihp %imana %imv > ") % (self.current_stats['hp'], self.current_stats['mana'], self.current_stats['movement']))

    def _setup_events(self):

        def _tick(_event):
            self._prompt()

        mud.__self__.on("tick", _tick)