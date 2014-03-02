from .. import actor, mud

def load(name):
    mud.safe_load("users", name)

def is_valid_name(name):
    name_len = len(name)
    return name.isalpha() and name_len > 2 and name_len < 12

class User(actor.Actor):

    def __init__(self):

        super(User, self).__init__()

    def input(self, event, client, args):
    
        command_name = args[0]
        command_args = args[1:]

        command = mud.safe_load("commands", command_name)

        if command:
            self._perform(command)
            event.handle()

    def _perform(self, command):
        pass