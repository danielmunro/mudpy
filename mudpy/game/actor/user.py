import time, __main__
from . import actor, disposition
from .. import room, command
from ...sys import wireframe, debug

def load(name):
    """Attempts to load a user from the user save file. If the file does
    not exist, the client is trying to create a new user.

    """
    from . import ability

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
        __main__.__mudpy__.fire('actor_enters_realm', self)

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
            hp_percent = self.target.curhp / self.target.get_attribute('hp')
            if hp_percent < 0.1:
                description = 'is in awful condition'
            elif hp_percent < 0.15:
                description = 'looks pretty hurt'
            elif hp_percent < 0.30:
                description = 'has some big nasty wounds and scratches'
            elif hp_percent < 0.50:
                description = 'has quite a few wounds'
            elif hp_percent < 0.75:
                description = 'has some small wounds and bruises'
            elif hp_percent < 0.99:
                description = 'has a few scratches'
            else:
                description = 'is in excellent condition'
            self.notify(str(self.target).title()+' '+description+'.\n')

    def add_affect(self, aff):
        super(User, self).add_affect(aff)
        self.notify(aff.messages['start']['self'])
    
    def tick(self, _event = None):
        super(User, self).tick()
        self.notify()
    
    def level_up(self):
        super(User, self).level_up()
        self.notify(actor.__config__['messages']['level_up'])

    def perform_ability(self, ability):
        """Applies delay to the user when performing an ability."""
        self.delay_counter += ability.delay+1

    def input(self, event, subscriber, args):
        return command.check_input(event, subscriber, args)

    def loggedin(self):
        """Miscellaneous setup tasks for when a user logs in. Nothing too
        exciting.

        """

        __main__.__mudpy__.fire("actor_enters_realm", self)

        # on server events
        __main__.__mudpy__.on('stat', self.stat)
        __main__.__mudpy__.on('cycle', self._update_delay)

        self.on('attacked', self._attacked)
        self.on('action', self._check_if_incapacitated)

        self.get_room().arriving(self)

        command.look(self)

        # on listeners to client input for abilities
        for ability in self.get_abilities():
            ability.on('perform', self.perform_ability)
            if ability.hook == 'input':
                def check_input(event, user, args):
                    """Checks if the user is trying to perform an ability with
                    a given input.

                    """

                    if ability.name.startswith(args[0]):
                        ability.try_perform(self, args[1:])
                        event.handle()
                self.client.on('input', check_input)

        debug.log(str(self.client)+' logged in as '+str(self))

    def sunset(self, _event, changed):
        """Notifies the user when a calendar event happens."""

        self.notify(changed)

    def sunrise(self, _event, changed):
        """Notifies the user when a calendar event happens."""

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

    def _attacked(self, event, attacker):
        self.notify("%s screams and attacks!" % attacker)

    def _end_affect(self, _event, affect):
        super(User, self)._end_affect(_event, affect)
        self.notify(affect.messages['end']['self'])
    
    def _normalize_stats(self, _event = None, _args = None):
        if self.curhp < -9:
            self._die()
        elif self.curhp <= 0:
            self.disposition = disposition.__incapacitated__
            self.notify(actor.__config__['messages']['incapacitated'])
        elif self.disposition == disposition.__incapacitated__ and self.curhp > 0:
            self.disposition = disposition.__laying__
            self.notify(actor.__config__['messages']['recover_from_incapacitation'])
        super(User, self)._normalize_stats()
    
    def _die(self):
        super(User, self)._die()
        self.get_room().leaving(self)
        self.room = room.__config__['start_room']
        self.get_room().arriving(self)
        self.notify(actor.__config__['messages']['died'])
    
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

    def _check_if_incapacitated(self, event, _action):
        """Don't let the actor do anything if they are incapacitated."""

        if self.disposition == disposition.__incapacitated__:
            self.notify(__config__['messages']['incapacitated'])
            event.handle()

    @classmethod
    def to_yaml(self, dumper, thing):
        import copy
        persist = copy.copy(thing)
        del persist.client
        return super(User, self).to_yaml(dumper, persist)

    def __str__(self):
        return self.name.title()
