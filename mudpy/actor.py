"""The actor module defines users and mobs and how they interact with the world.

"""

from __future__ import division
import time, random, __main__

from . import debug, room, server, item, collection, calendar, wireframe, \
        observer

# Needed for creating these things from wireframes -- hacky
from . import command, affect

__SAVE_DIR__ = 'data'
__config__ = None
__proxy__ = observer.Observer()

def broadcast_to_mudpy(*args):
    """This function is used as a callback to proxy messages from actors to the
    main game object, if it exists.
    
    """
    __main__.__mudpy__.dispatch(args[0], *args)

if '__mudpy__' in __main__.__dict__:

    def initialize_actor():
        global __config__
        __config__ = wireframe.create('config.actor')

    __proxy__.attach('__any__', broadcast_to_mudpy)
    __main__.__mudpy__.attach('initialize', initialize_actor)
    
def get_damage_verb(dam_roll):
    """A string representation of the severity of damage dam_roll will cause.

    """

    if dam_roll < 5:
        return "clumsy"
    elif dam_roll < 10:
        return "amateur"
    elif dam_roll < 15:
        return "competent"
    else:
        return "skillful"

def get_default_attributes():
    """Starting attributes for level 1 actors."""

    attr = {}
    attr['hp'] = 20
    attr['mana'] = 100
    attr['movement'] = 100
    attr['ac_bash'] = 100
    attr['ac_pierce'] = 100
    attr['ac_slash'] = 100
    attr['ac_magic'] = 100
    attr['hit'] = 1
    attr['dam'] = 1
    return attr

def get_attr_mod(actor, attribute_name):
    """Returns a small integer to be used in fight calculations."""

    return (actor.get_attribute(attribute_name) / Actor.MAX_STAT) * 4

class Actor(wireframe.Blueprint):
    """Abstract 'person' in the game, base object for users and mobs."""
    MAX_STAT = 25
    stats = ['str', 'int', 'wis', 'dex', 'con', 'cha']

    def __init__(self):
        self.name = ""
        self.title = "an actor"
        self.long = ""
        self.description = ""
        self.level = 0
        self.experience = 0
        self.experience_per_level = 1000
        self.alignment = 0
        self.attributes = get_default_attributes()
        self.curhp = self.attributes['hp']
        self.curmana = self.attributes['mana']
        self.curmovement = self.attributes['movement']
        self.sex = "neutral"
        self.room = 1
        self.abilities = []
        self.affects = []
        self.target = None
        self.inventory = item.Inventory()
        self.race = None
        self.trains = 0
        self.practices = 0
        self.disposition = Disposition.STANDING
        self.proficiencies = {}
        self.attacks = ['reg']
        self.last_command = None
        self.observers = {}
        
        self.equipped = dict((position, None) for position in ['light',
            'finger0', 'finger1', 'neck0', 'neck1', 'body', 'head', 'legs',
            'feet', 'hands', 'arms', 'torso', 'waist', 'wrist0', 'wrist1',
            'wield0', 'wield1', 'float'])

    def get_room(self, direction = ""):
        """Returns the current room the actor is in."""

        return room.get(self.room, direction)

    def get_proficiency(self, _proficiency):
        """Checks if an actor has a given proficiency and returns the object
        if successfully found.

        """

        for prof in self._get_proficiencies():
            if(prof.name == _proficiency):
                return prof
    
    def get_equipment_by_position(self, position):
        """Returns what the actor has equipped for requested position."""

        for _position in self.equipped:
            if _position.find(position) == 0:
                return self.equipped[_position]
    
    def set_equipment(self, equipment):
        """Equips an item, allowing the actor to take advantage of its
        properties.

        """

        return self._set_equipment_by_position(equipment.position, equipment)
    
    def get_wielded_weapons(self):
        """Helper function to return the weapons the actor has wielded."""

        return list(equipment for equipment in [self.equipped['wield0'], self.equipped['wield1']] if equipment)
    
    def notify(self, message = "", add_prompt = True):
        """Called to tell the actor a generic message. Only utilized by the 
        user class for transporting messages to the client.

        """

        pass

    def get_attribute(self, attribute_name):
        """Calculates the value of the attribute_name passed in, based on a
        number of variables, such as the starting attribute value, plus the
        trained values, racial modifiers, and affect modifiers.

        """

        amount = self._get_unmodified_attribute(attribute_name)
        for _affect in self.affects:
            amount += _affect.get_attribute(attribute_name)
        for equipment in self.equipped.values():
            if equipment:
                amount += getattr(equipment.attributes, attribute_name)
        if attribute_name in Actor.stats:
            return min(amount, self.get_max_attribute(attribute_name))
        return amount

    def get_max_attribute(self, attribute_name):
        """Returns the max attainable value for an attribute."""

        racial_attr = self.race.get_attribute(attribute_name)
        return min(
                self._attribute(attribute_name) + racial_attr + 4, 
                racial_attr + 8)
    
    def get_abilities(self):
        """Returns abilities available to the actor, including known ones and
        ones granted from racial bonuses.

        """

        return self.abilities + self.race.abilities

    def __str__(self):
        return self.title
    
    def status(self):
        """A string representation of the approximate physical health of the
        actor, based on the percentage of hp remaining.

        """

        hppercent = self.curhp / self.get_attribute('hp')
        
        if hppercent < 0.1:
            description = 'is in awful condition'
        elif hppercent < 0.15:
            description = 'looks pretty hurt'
        elif hppercent < 0.30:
            description = 'has some big nasty wounds and scratches'
        elif hppercent < 0.50:
            description = 'has quite a few wounds'
        elif hppercent < 0.75:
            description = 'has some small wounds and bruises'
        elif hppercent < 0.99:
            description = 'has a few scratches'
        else:
            description = 'is in excellent condition'

        return str(self).title()+' '+description+'.'

    def get_alignment(self):
        """A string representation of the actor's alignment. Alignment is
        changed based on the actor's actions.

        """

        if self.alignment <= -1000:
            return "evil"
        elif self.alignment <= 0:
            return "neutral"
        elif self.alignment >= 1000:
            return "good"
    
    def looked_at(self):
        """What a user sees when they look at the actor."""

        return self.long if self.long else str(self)+" the "+str(self.race)+" is "+self.disposition+" here."

    def add_affect(self, aff):
        """Apply an affect to the actor."""

        try:
            self.dispatch('changed', aff, self, aff.messages['start']['all'] % self)
        except KeyError:
            pass

        self.affects.append(aff)

        # for any modifiers that are percents, we need to 
        # get the percent of the actor's attribute
        for attr in aff.attributes:
            modifier = aff.get_attribute(attr)
            if modifier > 0 and modifier < 1:
                aff.attributes[attr] = self.get_attribute(attr) * modifier

        if aff.timeout > -1:
            __main__.__mudpy__.attach('tick', aff.countdown_timeout)
            aff.attach('end', self._end_affect)

    def set_target(self, target = None):
        """Sets up a new target for the actor."""

        if not target:
            self.target.detach('attack_resolution', self._normalize_stats)
            self.target = None
            return
        
        # target acquired
        self.target = target

        # handles above 100% hp/mana/mv and below 0% hp/mana/mv
        self.target.attach('attack_resolution', self._normalize_stats)

        # calls attack rounds until target is removed
        __main__.__mudpy__.attach('pulse', self._do_regular_attacks)
    
    def has_enough_movement(self):
        return self._get_movement_cost() <= self.curmovement

    def can_see(self):
        """Can the user see?"""

        if self.disposition is Disposition.SLEEPING:
            return False

        _room = self.get_room()

        if self.has_affect('glow'):
            return True

        if _room.get_area().location == room.__LOCATION_OUTSIDE__ and \
                calendar.__instance__.daylight:
            return True

        return _room.lit

    def qualifies_for_level(self):
        return self.experience / self.experience_per_level > self.level

    def level_up(self):
        """Increase the actor's level."""

        self.level += 1

        con = self._attribute('con')
        wis = self._attribute('wis')
        _str = self._attribute('str')

        self.attributes['hp'] += random.randint(con-4, con+4)
        self.attributes['mana'] += random.randint(wis*.5, wis*1.5)
        self.attributes['movement'] += random.randint(_str*.5, _str*1.5)

    def is_incapacitated(self):
        return self.disposition == Disposition.INCAPACITATED

    def sit(self):
        self.disposition = Disposition.SITTING

    def wake(self):
        self.disposition = Disposition.STANDING
    
    def sleep(self):
        self.disposition = Disposition.SLEEPING

    def has_affect(self, name):
        return collection.find(name, self.get_affects())

    def get_affects(self):
        """Returns all affects currently applied to the actor, including base
        affects and affects from equipment.

        """

        affects = list(self.affects)
        for _pos, equipment in self.equipped.iteritems():
            if equipment:
                affects += equipment.affects
        return affects
    
    def tick(self):
        """Called on the actor by the server, part of a series of "heartbeats".
        Responsible for regening the actor's hp, mana, and movement.
        
        """

        modifier = random.uniform(0.05, 0.125)
        if self.disposition == Disposition.INCAPACITATED:
            modifier = -modifier
        elif self.disposition == Disposition.LAYING:
            modifier += random.uniform(0.01, 0.05)
        elif self.disposition == Disposition.SLEEPING:
            modifier += random.uniform(0.05, 0.1)
        self.curhp += self.get_attribute('hp') * modifier
        self.curmana += self.get_attribute('mana') * modifier
        self.curmovement += self.get_attribute('movement') * modifier
        self._normalize_stats()

    def _check_if_incapacitated(self, action):

        if self.is_incapacitated():
            self.notify(__config__.messages['move_failed_incapacitated'])
            return True

    def _end_affect(self, affect):
        """Called when an affect ends."""

        self.affects.remove(affect)
        try:
            self.dispatch('changed', affect, self, affect.messages['end']['all'] % self)
        except KeyError:
            pass

    def _attribute(self, attr):
        return self.attributes[attr] if attr in self.attributes else 0
    
    def _get_proficiencies(self):
        """Returns all actor's proficiencies, including known ones and ones
        granted from racial bonuses.

        """

        all_proficiencies = dict(self.proficiencies)
        all_proficiencies.update(self.race.proficiencies)
        return all_proficiencies
    
    def _get_max_weight(self):
        """Returns the maximum weight that an actor can carry."""

        return 100+(self.level*100)
    
    def _is_encumbered(self):
        """If an actor is encumbered, certain tasks become more difficult."""

        return self.inventory.get_weight() > self._get_max_weight() * 0.95
    
    def _get_movement_cost(self):
        """Returns the movement cost of moving an actor from one room to
        an adjacent room.

        """

        if self._is_encumbered():
            return self.race.movement_cost + 1
        else:
            return self.race. movement_cost
    
    def _set_equipment_by_position(self, position, equipment):
        """Sets a piece of equipment by a specific position."""

        for _position in self.equipped:
            if _position.find(position) == 0:
                self.equipped[_position] = equipment
                return True
        return False
    
    def _normalize_stats(self, _args = None):
        """Ensures hp, mana, and movement do not exceed their maxes during a
        tick.

        """

        for attr in ['hp', 'mana', 'movement']:
            maxstat = self.get_attribute(attr)
            actorattr = 'cur'+attr
            if getattr(self, actorattr) > maxstat:
                setattr(self, actorattr, maxstat)

    def _get_unmodified_attribute(self, attribute_name):
        """Returns the "base" value of the requested attribute, which consists
        of the starting actor value plus trained amounts and racial bonuses.

        """

        return self._attribute(attribute_name) + \
                self.race.get_attribute(attribute_name)
    
    def _do_regular_attacks(self, recursed_attack_index = 0):
        """Recurse through the attacks the user is able to make for a round of
        battle.

        """

        if self.target:
            if not self.target.target:
                self.target.set_target(self)

            if self.disposition != Disposition.INCAPACITATED:
                try:
                    Attack(self, self.attacks[recursed_attack_index])
                    self._do_regular_attacks(recursed_attack_index + 1)
                except IndexError:
                    pass
        else:
            __main__.__mudpy__.detach('pulse', self._do_regular_attacks)

    def _end_battle(self):
        """Ensure the actor is removed from battle, unless multiple actors are
        targeting this actor.

        """

        for _actor in self.get_room().actors:
            if _actor.target is self:
                _actor.set_target()
        self.set_target()
    
    def _die(self):
        """What happens when the user is killed (regardless of the method of
        death). Does basic things such as creating the corpse and dispatching
        a disposition change event.
        
        """

        self.get_room().announce({
            self: "You died!!",
            "all": "%s died!" % str(self).title()
        })
        if self.target:
            # calculate the kill experience
            leveldiff = self.level - self.target.level
            experience = 200 + 30 * leveldiff
            if leveldiff > 5:
                experience *= 1 + random.randint(0, leveldiff*2) / 100
            aligndiff = abs(self.alignment - self.target.alignment) / 2000
            if aligndiff > 0.5:
                mod = random.randint(15, 35) / 100
                experience *= 1 + aligndiff - mod
            experience = int(round(random.uniform(experience * 0.8, experience * 1.2)))
            experience = experience if experience > 0 else 0

            # award experience and check for level change
            self.target.experience += experience
            self.target.notify("You gained "+str(experience)+" experience points.")
            if self.target.qualifies_for_level():
                self.target.notify(__config__.messages["qualifies_for_level"])
            self._end_battle()
        self.disposition = Disposition.LAYING
        self.curhp = 1
        corpse = item.Corpse()
        corpse.name = "the corpse of "+str(self)
        corpse.description = "The corpse of "+str(self)+" lies here."
        corpse.weight = self.race.size * 20
        corpse.material = "flesh"
        for i in self.inventory.items:
            self.inventory.remove(i)
            corpse.inventory.append(i)
        self.get_room().inventory.append(corpse)

class Mob(Actor):
    """NPCs of the game, mobs are the inhabitants of the mud world."""

    ROLE_TRAINER = 'trainer'
    ROLE_ACOLYTE = 'acolyte'

    yaml_tag = "u!mob"

    def __init__(self):
        self.movement = 0
        self.movement_timer = self.movement
        self.respawn = 1
        self.respawn_timer = self.respawn
        self.auto_flee = False
        self.start_room = None
        super(Mob, self).__init__()

    def room_update(self, actor):
        """Event listener for when the room update fires."""

        pass
    
    def tick(self):
        super(Mob, self).tick()
        if self.movement:
            self._decrement_movement_timer()
    
    def _decrement_movement_timer(self):
        """Counts down to 0, at which point the mob will attempt to move from
        their current room to a new one. They cannot move to new areas however.

        """

        self.movement_timer -= 1
        if self.movement_timer < 0:
            direction = random.choice([direction for direction, _room in 
                self.get_room().directions.iteritems() if _room and 
                _room.area == self.get_room().area])
            self.move(direction)
            self.movement_timer = self.movement
    
    def _normalize_stats(self, _args = None):
        if self.curhp < 0:
            self._die()
        super(Mob, self)._normalize_stats()
    
    def _die(self):
        super(Mob, self)._die()
        self.get_room().move_actor(self)
        room.get(room.__PURGATORY__).arriving(self)
        __main__.__mudpy__.attach('tick', self._respawn)

    def _respawn(self):
        self.respawn_timer -= 1
        if self.respawn_timer < 0:
            __main__.__mudpy__.detach('tick', self._respawn)
            self.disposition = Disposition.STANDING
            self.curhp = self.get_attribute('hp')
            self.curmana = self.get_attribute('mana')
            self.curmovement = self.get_attribute('movement')
            self.get_room().move_actor(self)
            room.get(self.start_room).arriving(self)
    
class User(Actor):
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

    def prompt(self):
        """The status prompt for a user. By default, shows current hp, mana,
        and movement. Not yet configurable."""

        return "%i %i %i >> " % (self.curhp, self.curmana, self.curmovement)
    
    def notify(self, message = "", add_prompt = True):
        if self.client.user:
            self.client.write(str(message)+"\n"+(self.prompt() if add_prompt \
                    else ""))
    
    def stat(self):
        """Notifies the user of the target's status (if any) and supplies a
        fresh prompt.

        """

        if self.target:
            self.notify(self.target.status()+"\n")

    def add_affect(self, aff):
        super(User, self).add_affect(aff)
        self.notify(aff.messages['start']['self'])
    
    def tick(self):
        super(User, self).tick()
        self.notify()

    def _end_affect(self, affect):
        super(User, self)._end_affect(affect)
        self.notify(affect.messages['end']['self'])
    
    def _normalize_stats(self, _args = None):
        if self.curhp < -9:
            self._die()
        elif self.curhp <= 0:
            self.disposition = Disposition.INCAPACITATED
            self.notify(__config__.messages['incapacitated'])
        elif self.disposition == Disposition.INCAPACITATED and self.curhp > 0:
            self.disposition = Disposition.LAYING
            self.notify(__config__.messages['recover_from_incapacitation'])
        super(User, self)._normalize_stats()
    
    def _die(self):
        super(User, self)._die()
        self.get_room()
        curroom.leaving(self)
        self.room = room.__START_ROOM__
        self.get_room().arriving(self)
        self.notify(__config__.messages['died'])
    
    def _update_delay(self):
        """Removes the client from polling for input if the user has a delay
        applied to it.

        """

        if self.delay_counter > 0:
            if not self.last_delay:
                __main__.__mudpy__.detach('cycle', self.client.poll)
            currenttime = int(time.time())
            if currenttime > self.last_delay:
                self.delay_counter -= 1
                self.last_delay = currenttime
        elif self.last_delay:
            __main__.__mudpy__.attach('cycle', self.client.poll)
            self.last_delay = 0
    
    def level_up(self):
        super(User, self).level_up()
        self.notify(__config__.messages['level_up'])

    def perform_ability(self, ability):
        """Applies delay to the user when performing an ability."""
        self.delay_counter += ability.delay+1

    def loggedin(self):
        """Miscellaneous setup tasks for when a user logs in. Nothing too
        exciting.

        """

        from . import command

        self.attach('action', self._check_if_incapacitated)
        __proxy__.dispatch("actor_enters_realm", self)

        # attach server events
        __main__.__mudpy__.attach('stat', self.stat)
        __main__.__mudpy__.attach('cycle', self._update_delay)

        self.get_room().arriving(self)

        command.look(self)

        # listener for client input to trigger commands in the game
        self.client.attach('input', command.check_input)

        # listeners for calendar events (sunrise, sunset) 
        calendar.__instance__.setup_listeners_for(self.calendar_changed)

        # attach listeners to client input for abilities
        for ability in self.get_abilities():
            ability.attach('perform', self.perform_ability)
            if ability.hook == 'input':
                def check_input(user, args):
                    """Checks if the user is trying to perform an ability with
                    a given input.

                    """

                    if ability.name.startswith(args[0]):
                        ability.try_perform(self, args[1:])
                        return True
                self.client.attach('input', check_input)

        debug.log('client logged in as '+str(self))

    def calendar_changed(self, calendar, changed):
        """Notifies the user when a calendar event happens, such as the sun
        rises.

        """

        self.notify(changed)

    def room_update(self, actor):
        """Event listener for when the room update fires."""

        if actor is self:
            if 'self' in actor.last_command.messages:
                self.notify(actor.last_command.messages['self'])
        elif self.can_see():
            if 'all' in actor.last_command.messages:
                self.notify(actor.last_command.messages['all'] % str(actor).title())

    @classmethod
    def to_yaml(self, dumper, thing):
        import copy
        persist = copy.copy(thing)
        del persist.client
        return super(User, self).to_yaml(dumper, persist)

    def save(self, args = []):
        """Persisting stuff."""

        if "area" in args:
            wireframe.save(self.get_room().get_area())
        else:
            wireframe.save(self, "data.users")

    @staticmethod
    def load(name):
        """Attempts to load a user from the user save file. If the file does
        not exist, the client is trying to create a new user.

        """

        try:
            return wireframe.create(name.capitalize(), "data.users")
        except wireframe.WireframeException:
            pass

    @staticmethod
    def is_valid_name(name):
        """Check if a user name is a valid format."""

        name_len = len(name)
        return name.isalpha() and name_len > 2 and name_len < 12

    def __str__(self):
        return self.name.title()

class Disposition:
    """Dispositions are physical stances the actor can have. They define which
    commands are available to the actor, and affect regen rates.

    """

    def __init__(self):
        pass

    STANDING = 'standing'
    SITTING = 'sitting'
    LAYING = 'laying'
    SLEEPING = 'sleeping'
    INCAPACITATED = 'incapacitated'

class Attack:
    """One attack object is created for each aggressor during an attack round
    to resolve all of that aggressor's attacks. The aggressor automatically
    targets the actor stored in aggressor.target.
    
    """

    def __init__(self, aggressor, attackname):
        self.aggressor = aggressor
        self.success = False
        self.hitroll = 0
        self.damroll = 0
        self.defroll = 0

        handled = self.aggressor.dispatch('attack_start', self)
        if handled:
            return

        # initial rolls for attack/defense
        hit_roll = aggressor.get_attribute('hit') + get_attr_mod(aggressor, 'dex')
        def_roll = get_attr_mod(aggressor.target, 'dex') / 2
        def_roll += 5 - aggressor.target.race.size

        # determine dam type from weapon
        weapons = aggressor.get_wielded_weapons()
        try:
            dam_type = weapons[0].damage_type
        except IndexError:
            dam_type = aggressor.race.dam_type

        # get the ac bonus from the damage type
        try:
            ac = aggressor.target.get_attribute('ac_'+dam_type) / 100
        except AttributeError:
            ac = 0

        self.aggressor.dispatch('attackmodifier', self)

        # roll the dice and determine if the attack was successful
        roll = random.uniform(hit_roll/2, hit_roll) - random.uniform(def_roll/2, def_roll) - ac

        self.success = roll > 0
        if self.success:
            is_hit = "hits"
            dam_roll = aggressor.get_attribute('dam') + get_attr_mod(aggressor, 'str')
            dam_roll = random.uniform(dam_roll/2, dam_roll)
        else:
            is_hit = "misses"
            dam_roll = 0

        # update the room on the attack progress
        verb = get_damage_verb(dam_roll)
        ucname = str(aggressor).title()
        tarname = str(aggressor.target)
        aggressor.get_room().announce({
            aggressor: "("+attackname+") Your "+verb+" attack "+is_hit+" "+tarname+".",
            aggressor.target: ucname+"'s "+verb+" attack "+is_hit+" you.",
            "all": ucname+"'s "+verb+" attack "+is_hit+" "+tarname+"."
        }, add_prompt = False)

        #need to do this check again here, can't have the actor dead before the hit message
        if roll > 0: 
            aggressor.target.curhp -= dam_roll

        aggressor.dispatch('attack_resolution', self)

class Ability(wireframe.Blueprint):
    """Represents something cool an actor can do. Invoked when the hook is
    triggered on the parent actor. Applies costs in the costs dict, and affects
    in the affects list.
    
    """

    yaml_tag = "u!ability"

    def __init__(self):
        self.name = "an ability"
        self.level = 0
        self.affects = []
        self.costs = {}
        self.delay = 0
        self.type = "" # skill or spell
        self.hook = ""
        self.aggro = False
        self.messages = {}
    
    def try_perform(self, invoker, args):
        """Parses the user input, finds a target, applies the ability cost,
        and invokes the ability.

        """

        receiver = None
        try:
            args = args[0]
            receiver = invoker.get_room().get_actor(args[-1])
        except IndexError:
            pass
        if not receiver:
            receiver = invoker
        if self.apply_cost(invoker):
            invoker.delay_counter += self.delay + 1
            success = random.randint(0, 1)
            if success:
                self.perform(receiver)
            else:
                invoker.notify('failed')
        else:
            invoker.notify(__config__.messages['apply_cost_fail'])

    def perform(self, receiver):
        """Initialize all the affects associated with this ability."""

        for affectname in self.affects:
            receiver.add_affect(wireframe.create(affectname))
    
    def apply_cost(self, invoker):
        """Iterates over the cost property, checks that all requirements are
        met, applies each cost, then returns true. If costs cannot be met by
        the invoking actor, this method will return false.

        """

        for attr, cost in self.costs.iteritems():
            curattr = getattr(invoker, 'cur'+attr)
            cost *= curattr if cost > 0 and cost < 1 else 1
            if curattr < cost:
                return False
        for attr, cost in self.costs.iteritems():
            curattr = getattr(invoker, 'cur'+attr)
            cost *= curattr if cost > 0 and cost < 1 else 1
            setattr(invoker, 'cur'+attr, curattr-cost)
        return True
    
    def __str__(self):
        return self.name

class Race(wireframe.Blueprint):
    """Gives various properties to an actor that have far reaching affects
    throughout the game.

    """

    yaml_tag = "u!race"

    SIZE_TINY = 1
    SIZE_SMALL = 2
    SIZE_NORMAL = 3
    SIZE_LARGE = 4
    SIZE_GIGANTIC = 5

    def __init__(self):
        self.name = "critter"
        self.size = self.SIZE_NORMAL
        self.movement_cost = 1
        self.is_playable = False
        self.dam_type = "bash"
        self.proficiencies = {}
        self.attributes = {}
        self.abilities = []
        self.affects = []

    def get_attribute(self, attribute):
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            return 0
    
    @classmethod
    def to_yaml(self, dumper, thing):
        import copy
        persist = copy.copy(thing)
        persist.__dict__ = {'wireframe': 'race.'+str(persist)}
        return super(Race, self).to_yaml(dumper, persist)

    def __str__(self):
        return self.name
