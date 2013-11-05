"""The actor module defines users and mobs and how they interact with the world.

"""

from __future__ import division
import random

from ...sys import collection, calendar, wireframe, observer
from .. import room, item
from .  import disposition, attack

__SAVE_DIR__ = 'data'
__config__ = None
__proxy__ = observer.Observer()
__mudpy__ = None

def broadcast_to_mudpy(*args):
    """This function is used as a callback to proxy messages from actors to the
    main game object, if it exists.
    
    """

    __mudpy__.fire(*args)

def initialize(mudpy):
    """Sets up the module level configuration object for this mud instance.
    
    """

    global __config__, __mudpy__

    __config__ = wireframe.create('config.actor')
    __mudpy__ = mudpy

__proxy__.on('__any__', broadcast_to_mudpy)

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

    def __init__(self):
        self.name = ""
        self.title = "an actor"
        self.long = ""
        self.description = ""
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
        super(Actor, self).__init__()
        
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

        racial_attr = self.race._attribute(attribute_name)
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
            self.fire('changed', aff, self, aff.messages['start']['all'] % self)
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
            __mudpy__.on('tick', aff.countdown_timeout)
            aff.on('end', self._end_affect)

    def set_target(self, target = None):
        """Sets up a new target for the actor."""

        if not target:
            self.target.off('attack_resolution', self._normalize_stats)
            self.target = None
            return
        
        # target acquired
        self.target = target

        # handles above 100% hp/mana/mv and below 0% hp/mana/mv
        self.target.on('attack_resolution', self._normalize_stats)

        # calls attack rounds until target is removed
        __mudpy__.on('pulse', self._do_regular_attacks)
    
    def has_enough_movement(self):
        return self._get_movement_cost() <= self.curmovement

    def can_see(self):
        """Can the user see?"""

        if self.disposition is disposition.__sleeping__:
            return False

        _room = self.get_room()

        if self.has_affect('glow'):
            return True

        if _room.get_area().location == room.__LOCATION_OUTSIDE__ and \
                calendar.__instance__.daylight:
            return True

        return _room.lit

    def qualifies_for_level(self):
        return self.experience / self._experience_per_level() > self.level

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
        self.disposition = disposition.__sitting__

    def wake(self):
        self.disposition = disposition.__standing__
    
    def sleep(self):
        self.disposition = disposition.__sleeping__

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
    
    def tick(self, _event = None):
        """Called on the actor by the server, part of a series of "heartbeats".
        Responsible for regening the actor's hp, mana, and movement.
        
        """

        modifier = random.uniform(0.05, 0.125)
        if self.disposition == disposition.__incapacitated__:
            modifier = -modifier
        elif self.disposition == disposition.__laying__:
            modifier += random.uniform(0.01, 0.05)
        elif self.disposition == disposition.__sleeping__:
            modifier += random.uniform(0.05, 0.1)
        self.curhp += self.get_attribute('hp') * modifier
        self.curmana += self.get_attribute('mana') * modifier
        self.curmovement += self.get_attribute('movement') * modifier
        self._normalize_stats()

    def actor_changed(self, _event, actor, message = ""):
        """Event listener for when the room update fires."""

        pass

    def _experience_per_level(self):
        return self.race.experience

    def _check_if_incapacitated(self, _event, _action):

        if self.disposition == disposition.__incapacitated__:
            self.notify(__config__.messages['move_failed_incapacitated'])
            return True

    def _end_affect(self, _event, affect):
        """Called when an affect ends."""

        self.affects.remove(affect)
        try:
            self.fire('changed', affect, self, affect.messages['end']['all'] % self)
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
    
    def _normalize_stats(self, _event = None, _args = None):
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
                self.race._attribute(attribute_name)
    
    def _do_regular_attacks(self, _event):
        """Recurse through the attacks the user is able to make for a round of
        battle.

        """

        if self.target and not self.disposition is disposition.__incapacitated__:
            if not self.target.target:
                self.target.set_target(self)
            attack.round(self)
        else:
            __mudpy__.off('pulse', self._do_regular_attacks)

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
        death). Does basic things such as creating the corpse and firing
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
        self.disposition = disposition.__laying__
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
