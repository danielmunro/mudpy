"""The actor module defines users and mobs and how they interact with the world.

"""

import random, __main__
from ...sys import collection, wireframe, debug, observer
from .. import room, item
from .  import disposition, attack

__SAVE_DIR__ = 'data'
__config__ = wireframe.create('config.actor')

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

class Actor(wireframe.Blueprint):
    """Abstract 'person' in the game, base object for users and mobs."""
    MAX_STAT = 25
    stats = ['str', 'int', 'wis', 'dex', 'con', 'cha']
    vitals = ['hp', 'mana', 'movement']

    def __init__(self):
        self.level = 0
        self.experience = 0
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
        self.disposition = disposition.__standing__
        self.proficiencies = {}
        self.attacks = ['reg']
        self.last_command = None

        if '__mudpy__' in dir(__main__):
            self.publisher = getattr(__main__, '__mudpy__')
        else:
            self.publisher = observer.Observer()

        self.publisher.on('tick', self.tick)

        super(Actor, self).__init__()

        self.equipped = dict((position, None) for position in ['light',
            'finger0', 'finger1', 'neck0', 'neck1', 'body', 'head', 'legs',
            'feet', 'hands', 'arms', 'torso', 'waist', 'wrist0', 'wrist1',
            'wield0', 'wield1', 'float'])

    def get_room(self, direction=""):
        """Returns the current room the actor is in."""

        return room.get(self.room, direction)

    def get_proficiency(self, proficiency_name):
        """Checks if an actor has a given proficiency and returns the object
        if successfully found.

        """

        return next(_proficiency for _proficiency in self._get_proficiencies()
                if _proficiency.name == proficiency_name)

    def get_equipment_by_position(self, position):
        """Returns what the actor has equipped for requested position."""

        return next(eq for pos, eq in self.equipped.items() \
                if pos.find(position) == 0)

    def set_equipment(self, equipment):
        """Equips an item, allowing the actor to take advantage of its
        properties.

        """

        return self._set_equipment_by_position(equipment.position, equipment)

    def get_wielded_weapons(self):
        """Helper function to return the weapons the actor has wielded."""

        return list(
            filter(None, [self.equipped['wield0'], self.equipped['wield1']]))

    def notify(self, *_args):
        """Called to tell the actor a generic message. Only utilized by the
        user class for transporting messages to the client.

        """

        pass

    def get_attribute(self, attribute_name):
        """Calculates the value of the attribute_name passed in, based on a
        number of variables, such as the starting attribute value, plus the
        trained values, and racial, equipment, and affect modifiers.

        """

        # base attribute amount
        amount = self._get_unmodified_attribute(attribute_name)

        # affect modifiers
        amount += self._get_modifiers(self.affects, attribute_name)

        # equipment modifiers
        eq = list(eq for eq in self.equipped.values() if eq)
        amount += self._get_modifiers(eq, attribute_name)

        # if a stat, don't let it exceed the maximum
        if attribute_name in Actor.stats:
            amount = min(amount, self._get_max_attribute(attribute_name))

        return amount

    def get_abilities(self):
        """Returns abilities available to the actor, including known ones and
        ones granted from racial bonuses.

        """

        return self.abilities + self.race.abilities

    def add_affect(self, aff):
        """Apply an affect to the actor."""

        try:
            self.fire('changed', aff, self, aff.messages['start']['all'] % self)
        except KeyError:
            pass

        self.affects.append(aff)

        if aff.timeout > -1:
            self.publisher.on('tick', aff.countdown_timeout)
            aff.on('end', self._end_affect)

    def set_target(self, target=None):
        """Sets up a new target for the actor."""

        if not target:
            self.target.off('attack_resolution', self._normalize_stats)
            self.target = None
            return

        # target acquired
        self.target = target

        handled = self.target.fire('attacked', self)

        if not handled:
            # handles above 100% hp/mana/mv and below 0% hp/mana/mv
            self.target.on('attack_resolution', self._normalize_stats)

            # calls attack rounds until target is removed
            self.publisher.on('pulse', self._do_regular_attacks)

    def has_enough_movement(self):
        """Return true if the user has enough movement points to leave the
        room.

        """

        return self._get_movement_cost() <= self.curmovement

    def can_see(self):
        """Can the user see?"""

        from ...sys import calendar

        if self.disposition is disposition.__sleeping__:
            return False

        if self.has_affect('glow'):
            return True

        _room = self.get_room()

        if _room.get_area().location == room.__LOCATION_OUTSIDE__ and \
                calendar.__instance__.daylight:
            return True

        return _room.lit

    def qualifies_for_level(self):
        """Return true if the actor has enough experience to level up."""

        return self.experience / self.experience_per_level() > self.level

    def level_up(self):
        """Increase the actor's level."""

        self.level += 1

        con = self._attribute('con')
        wis = self._attribute('wis')
        _str = self._attribute('str')

        self.attributes['hp'] += random.randint(con-4, con+4)
        self.attributes['mana'] += random.randint(wis*.5, wis*1.5)
        self.attributes['movement'] += random.randint(_str*.5, _str*1.5)

    def sit(self):
        """Make the actor sit down."""

        self.disposition = disposition.__sitting__

    def wake(self):
        """Make the actor wake up."""

        self.disposition = disposition.__standing__

    def sleep(self):
        """Make the actor go to sleep."""

        self.disposition = disposition.__sleeping__

    def has_affect(self, name):
        """Returns true if the actor has an affect applied that matches the
        given name.

        """

        return collection.find(name, self.get_affects())

    def __str__(self):
        return self.name

    def get_affects(self):
        """Returns all affects currently applied to the actor, including base
        affects and affects from equipment.

        """

        return self.affects + \
                list(eq.affects for pos, eq in self.equipped.items() if eq)

    def tick(self):
        """Called on the actor by the server, part of a series of "heartbeats".
        Responsible for regening the actor's hp, mana, and movement.

        """

        if self.disposition != disposition.__incapacitated__:
            modifier = disposition.get_regen_modifier(self.disposition)
            self.curhp += self.get_attribute('hp') * modifier
            self.curmana += self.get_attribute('mana') * modifier
            self.curmovement += self.get_attribute('movement') * modifier
            self._normalize_stats()

    def actor_changed(self):
        """Event listener for when the room update fires."""

        pass

    def end_battle(self):
        """Ensure the actor is removed from battle, unless multiple actors are
        targeting this actor.

        """

        for _actor in self.get_room().actors:
            if _actor.target is self:
                _actor.set_target()

        self.set_target()

    def experience_per_level(self):
        """Calculate the experience this actor needs in order to level."""

        return self.race.experience

    def _get_max_attribute(self, attribute_name):
        """Returns the max attainable value for an attribute."""

        if attribute_name in Actor.stats:
            attr = self._get_unmodified_attribute(attribute_name)
            return min(
                    attr + 4,
                    self.race._attribute(attribute_name) + 8)
        else:
            return -1

    def _get_modifiers(self, _list, attribute_name):
        """Takes a list of things with attributes and returns the sum of adding
        all modifiers together for a given attribute.

        """

        amount = 0

        for thing in _list:
            mod = thing.get_attribute(attribute_name)
            if isinstance(mod, float):
                mod = self._get_unmodified_attribute(attribute_name) * mod
            amount += mod

        return amount

    def _end_affect(self, event, affect):
        """Called when an affect ends."""

        self.affects.remove(affect)
        try:
            message = affect.messages['end']['all'] % self
            self.fire('changed', affect, self, message)
        except KeyError:
            pass
        event.handle()

    def _attribute(self, attr):
        """Helper to get attribute for actor."""

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

    def _normalize_stats(self):
        """Reset actor vitals to maxes periodically if they become exceeded."""

        for attr in Actor.vitals:
            maxstat = self.get_attribute(attr)
            actorattr = 'cur'+attr
            if getattr(self, actorattr) > maxstat:
                setattr(self, actorattr, maxstat)

    def _get_unmodified_attribute(self, attr):
        """Returns the "base" value of the requested attribute, which consists
        of the starting actor value plus trained amounts and racial bonuses.

        """

        return self._attribute(attr) + self.race._attribute(attr)

    def _do_regular_attacks(self, event):
        """Recurse through the attacks the user is able to make for a round of
        battle.

        """

        if self.target:
            if not self.target.target:
                self.target.set_target(self)
            if not self.disposition is disposition.__incapacitated__:
                attack.round(self)
        else:
            self.publisher.off('pulse', self._do_regular_attacks)
            event.handle()

    def _die(self):
        """What happens when the user is killed (regardless of the method of
        death). Does basic things such as creating the corpse and firing
        a disposition change event.

        """

        self.get_room().announce({
            self: "You died!!",
            "all": "%s died!" % str(self).title()
        }, False)
        if self.target:
            debug.info(str(self.target)+" killed "+str(self))
            # calculate the kill experience
            leveldiff = self.level - self.target.level
            experience = 200 + 30 * leveldiff
            if leveldiff > 5:
                experience *= 1 + random.randint(0, leveldiff*2) / 100
            aligndiff = abs(self.alignment - self.target.alignment) / 2000
            if aligndiff > 0.5:
                mod = random.randint(15, 35) / 100
                experience *= 1 + aligndiff - mod
            low = experience * 0.8
            high = experience * 1.2
            experience = int(round(random.uniform(low, high)))
            experience = experience if experience > 0 else 0

            # award experience and check for level change
            self.target.experience += experience
            message = __config__["messages"]["experience_gain"] % experience
            self.target.notify(message)
            if self.target.qualifies_for_level():
                message = __config__["messages"]["qualifies_for_level"]
                self.target.notify(message)
            self.end_battle()
        else:
            debug.info(str(self)+" died!")
        self.disposition = disposition.__laying__
        self.curhp = 1
        corpse = item.Corpse()
        corpse.name = "the corpse of "+str(self)
        corpse.short_desc = "The corpse of "+str(self)+" lies here."
        corpse.long_desc = corpse.short_desc
        corpse.weight = self.race.size * 20
        corpse.material = "flesh"
        for i in self.inventory.items:
            self.inventory.remove(i)
            corpse.inventory.append(i)
        self.get_room().inventory.append(corpse)
