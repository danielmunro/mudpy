import __main__
from . import actor, disposition
from ...sys import wireframe, debug

# wireframe import hack -- figure out how to remove later
from . import ability
from .. import command

def load(name):
    """Attempts to load a user from the user save file. If the file does
    not exist, the client is trying to create a new user.

    """

    try:
        return wireframe.create(name.capitalize(), "data.users")
    except wireframe.WireframeException:
        pass

def is_valid_name(name):
    """Check if a user name is a valid format."""

    name_len = len(name)
    return name.isalpha() and name_len > 2 and name_len < 12

class User(actor.Actor):
    """The actor controlled by a client connected by the server."""

    yaml_tag = "u!user"

    def __init__(self):
        self.delay_counter = 0
        self.last_delay = 0
        self.trains = 5
        self.practices = 5
        self.client = None
        self.observers = {}
        self.role = 'player'
        super(User, self).__init__()

        # listeners for calendar events (sunrise, sunset) 
        # @todo remove tight coupling
        from ...sys import calendar
        calendar.__instance__.setup_listeners_for(self.calendar_changed)
        self.on('action', self._check_if_incapacitated)

    def prompt(self):
        """The status prompt for a user. By default, shows current hp, mana,
        and movement. Not yet configurable."""

        return "%i %i %i >> " % (self.curhp, self.curmana, self.curmovement)
    
    def notify(self, message = "", add_prompt = True):
        if self.client.user:
            self.client.write(str(message)+"\n"+(self.prompt() if add_prompt \
                    else ""))
    
    def stat(self, _event = None):
        """Notifies the user of the target's status (if any) and supplies a
        fresh prompt.

        """

        if self.target:
            self.notify(self.target.status()+"\n")

    def add_affect(self, aff):
        super(User, self).add_affect(aff)
        self.notify(aff.messages['start']['self'])
    
    def tick(self, _event = None):
        super(User, self).tick()
        self.notify()
    
    def level_up(self):
        super(User, self).level_up()
        self.notify(__config__.messages['level_up'])

    def perform_ability(self, ability):
        """Applies delay to the user when performing an ability."""
        self.delay_counter += ability.delay+1

    def input(self, event, subscriber, args):
        return command.check_input(event, subscriber, args)

    def loggedin(self, _event, user):
        """Miscellaneous setup tasks for when a user logs in. Nothing too
        exciting.

        """

        actor.__proxy__.fire("actor_enters_realm", self)

        # on server events
        __main__.__mudpy__.on('stat', self.stat)
        __main__.__mudpy__.on('cycle', self._update_delay)

        self.get_room().arriving(self)

        command.look(self)

        # on listeners to client input for abilities
        for ability in self.get_abilities():
            ability.on('perform', self.perform_ability)
            if ability.hook == 'input':
                def check_input(user, _event, args):
                    """Checks if the user is trying to perform an ability with
                    a given input.

                    """

                    if ability.name.startswith(args[0]):
                        ability.try_perform(self, args[1:])
                        return True
                self.client.on('input', check_input)

        debug.log('user logged in as '+str(self))

    def calendar_changed(self, calendar, changed):
        """Notifies the user when a calendar event happens, such as the sun
        rises.

        """

        self.notify(changed)

    def actor_changed(self, _event, actor, message = ""):
        """Event listener for when the room update fires."""

        if actor is not self and self.can_see():
            if message:
                self.notify(message)

    def save(self, args = []):
        """Persisting stuff."""

        if "area" in args:
            wireframe.save(self.get_room().get_area())
        else:
            wireframe.save(self, "data.users")

    def _end_affect(self, _event, affect):
        super(User, self)._end_affect(_event, affect)
        self.notify(affect.messages['end']['self'])
    
    def _normalize_stats(self, _args = None):
        if self.curhp < -9:
            self._die()
        elif self.curhp <= 0:
            self.disposition = disposition.__incapacitated__
            self.notify(__config__.messages['incapacitated'])
        elif self.disposition == disposition.__incapacitated__ and self.curhp > 0:
            self.disposition = disposition.__laying__
            self.notify(__config__.messages['recover_from_incapacitation'])
        super(User, self)._normalize_stats()
    
    def _die(self):
        super(User, self)._die()
        self.get_room()
        curroom.leaving(self)
        self.room = room.__START_ROOM__
        self.get_room().arriving(self)
        self.notify(__config__.messages['died'])
    
    def _update_delay(self, _event = None):
        """Removes the client from polling for input if the user has a delay
        applied to it.

        """

        if self.delay_counter > 0:
            if not self.last_delay:
                __main__.__mudpy__.off('cycle', self.client.poll)
            currenttime = int(time.time())
            if currenttime > self.last_delay:
                self.delay_counter -= 1
                self.last_delay = currenttime
        elif self.last_delay:
            __main__.__mudpy__.on('cycle', self.client.poll)
            self.last_delay = 0

    @classmethod
    def to_yaml(self, dumper, thing):
        import copy
        persist = copy.copy(thing)
        del persist.client
        return super(User, self).to_yaml(dumper, persist)

    def __str__(self):
        return self.name.title()
