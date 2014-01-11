import time
from . import actor, disposition
from . import ability # hacky, needed by wireframe parsing
from .. import room, command
from ...sys import wireframe, debug

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
        self.trains = 5
        self.practices = 5
        self.client = None
        self.observers = {}
        self.role = 'player'
        super().__init__()

    def prompt(self):
        """The status prompt for a user. By default, shows current hp, mana,
        and movement. Not yet configurable."""

        return "%i %i %i >> " % (self.curhp, self.curmana, self.curmovement)

    def notify(self, message="", add_prompt=True):
        self.client.write(str(message)+"\n"+("\n"+self.prompt() if add_prompt else ""))

    def add_affect(self, aff):
        super(User, self).add_affect(aff)
        self.notify(aff.messages['start']['self'])

    def tick(self, _event=None):
        super(User, self).tick()
        self.notify()

    def level_up(self):
        super(User, self).level_up()
        self.notify(actor.__config__['messages']['level_up'])

    def loggedin(self, client):
        """Miscellaneous setup tasks for when a user logs in. Nothing too
        exciting.

        """

        def _unlisten_tick(*_args):
            self.publisher.off('tick', self.tick)

        def _stat(*_args):
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
                self.notify(str(self.target).title()+' '+description+'.')

        def _update_delay(*_args):
            """Removes the client from polling for input if the user has a delay
            applied to it.

            """

            if self.delay_counter > 0:
                if self.client.activated:
                    self.client.deactivate()
                self.delay_counter -= 1
            elif not self.client.activated:
                self.client.activate()

        def _check_if_incapacitated(event, *_args):
            """Don't let the actor do anything if they are incapacitated."""

            if self.disposition == disposition.__incapacitated__:
                self.notify(__config__['messages']['incapacitated'])
                event.handle()

        def _add_delay(event):
            """Applies delay to the user when performing an ability."""

            self.delay_counter += event.publisher.delay

        def _announce_arrival(event, logged_in):
            self.notify(actor.__config__['messages'][event.name] % str(logged_in).title())

        def _input(event, input_user, args):
            return command.check_input(event, input_user, args)

        self.client = client
        self.client.on('input', _input)

        self.on('actor_leaves_realm', _unlisten_tick)
        self.on('action', _check_if_incapacitated)

        self.publisher.fire('actor_enters_realm', self)

        self.publisher.on('stat', _stat)
        self.publisher.on('pulse', _update_delay)
        self.publisher.on('actor_enters_realm', _announce_arrival)

        self.get_room().arriving(self)

        command.do(self, 'look')

        # on listeners to client input for abilities
        for ability in self.get_abilities():
            ability.on('perform', _add_delay)
            if ability.hook == 'input':
                def _check_input(event, user, args):
                    """Checks if the user is trying to perform an ability with
                    a given input.

                    """

                    if ability.name.startswith(args[0]):
                        ability.try_perform(self, args[1:])
                        event.handle()
                self.client.on('input', _check_input)

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

    def _end_affect(self, _event, affect):
        super(User, self)._end_affect(_event, affect)
        self.notify(affect.messages['end']['self'])

    def _normalize_stats(self, _event=None, _args=None):
        if self.curhp < -9:
            self._die()
        elif self.curhp <= 0 and self.disposition != disposition.__incapacitated__:
            self.disposition = disposition.__incapacitated__
            self.notify(actor.__config__['messages']['incapacitated'], False)
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

    @classmethod
    def to_yaml(self, dumper, thing):
        import copy
        persist = copy.copy(thing)
        del persist.client
        return super(User, self).to_yaml(dumper, persist)

    def __str__(self):
        return self.name.title()
