from .. import actor, mud

def load(name):
    mud.safe_load("users", name)

def is_valid_name(name):
    name_len = len(name)
    return name.isalpha() and name_len > 2 and name_len < 12

class User(actor.Actor):

    yaml_tag = "user"
    __starting_hp__ = 20
    __starting_mana__ = 100
    __starting_movement__ = 100
    __starting_luck__ = 100

    def __init__(self, publisher):

        self.client = None

        super(User, self).__init__(publisher)

        self.add_to_attr('hp', self.__starting_hp__)
        self.add_to_attr('mana', self.__starting_mana__)
        self.add_to_attr('movement', self.__starting_movement__)
        self.add_to_attr('luck', self.__starting_luck__)

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

    def look(self, _args = None):

        _room = self.room
        msg = "%s\n%s\n\n" % (_room.short_desc, _room.long_desc)
        msg += "".join(
                    str(_actor).capitalize()+" is "+_actor.disposition+" here.\n"
                        for _actor in _room.actors if _actor is not actor)
        self.notify(msg.strip())

    def _prompt(self, *_args):
        self.notify(("\n\n%ihp %imana %imv > ") % (self.stats['hp'], self.stats['mana'], self.stats['movement']))

    def _setup_events(self):

        def _tick(_event):
            self._prompt()

        self.room = self.publisher.__rooms__[actor.__start_room__]

        self.publisher.on("tick", _tick)

        super(User, self)._setup_events()