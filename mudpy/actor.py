"""The actor module is the 'meat' of the framework, defines users and mobs and
how they interact with the world.

"""

from __future__ import division
from . import debug, room, utility, server, proficiency, item, \
                attributes, observer, command, affect, calendar, wireframe
import time, random, os, pickle, re, yaml

__SAVE_DIR__ = 'data'
__config__ = None
    
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

class Actor(observer.Observer, yaml.YAMLObject):
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
        self.experience_per_level = 0
        self.alignment = 0
        self.attributes = get_default_attributes()
        self.trained_attributes = {}
        self.curhp = self.attributes['hp']
        self.curmana = self.attributes['mana']
        self.curmovement = self.attributes['movement']
        self.sex = "neutral"
        self.room = None
        self.room_id = 0 # we only save the room id, not the room itself
        self.abilities = []
        self.affects = []
        self.target = None
        self.inventory = item.Inventory()
        self.race = None
        self.trains = 0
        self.practices = 0
        self.disposition = Disposition.STANDING
        self.proficiencies = dict()
        self.attacks = ['reg']
        self.set_experience_per_level()
        
        self.equipped = dict((position, None) for position in ['light',
            'finger0', 'finger1', 'neck0', 'neck1', 'body', 'head', 'legs',
            'feet', 'hands', 'arms', 'torso', 'waist', 'wrist0', 'wrist1',
            'wield0', 'wield1', 'float'])

        # listener for the server tick
        server.__instance__.heartbeat.attach('tick', self._tick)

    def _attribute(self, attr):
        try:
            return self.attributes[attr]
        except KeyError:
            return 0

    def get_proficiency(self, _proficiency):
        """Checks if an actor has a given proficiency and returns the object
        if successfully found.

        """

        for prof in self._get_proficiencies():
            if(prof.name == _proficiency):
                return prof
    
    def add_proficiency(self, _proficiency, level):
        """Adds a proficiency to the actor."""

        _proficiency = str(proficiency)
        try:
            self.proficiencies[_proficiency].level += level
        except KeyError:
            self.proficiencies[_proficiency] = wireframe.create(_proficiency)
            self.proficiencies[_proficiency].level = level
    
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
            amount += getattr(_affect.attributes, attribute_name)
        for equipment in self.equipped.values():
            if equipment:
                amount += getattr(equipment.attributes, attribute_name)
        if attribute_name in Actor.stats:
            return min(amount, self.get_max_attribute(attribute_name))
        return amount

    def get_trained_attribute(self, attribute):
        try:
            return self.trained_attributes[attribute]
        except KeyError:
            return 0

    def get_max_attribute(self, attribute_name):
        """Returns the max attainable value for an attribute."""

        racial_attr = self.race.get_attribute(attribute_name)
        return min(
                getattr(self.attributes, attribute_name) + racial_attr + 4, 
                racial_attr + 8)
    
    def get_abilities(self):
        """Returns abilities available to the actor, including known ones and
        ones granted from racial bonuses.

        """

        return self.abilities + self.race.abilities

    def __str__(self):
        return self.title
    
    def get_wielded_weapons(self):
        """Helper function to return the weapons the actor has wielded."""

        return list(equipment for equipment in [self.equipped['wield0'], self.equipped['wield1']] if equipment)
    
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
    
    def move(self, direction = None):
        """Try to move the actor in the given direction."""
        direction = direction or random.choice([direction for direction, _room 
            in self.room.directions.iteritems() if _room])

        if self.target:
            self.notify(__config__.messages['move_failed_fighting'])
            return

        if self.disposition == Disposition.INCAPACITATED:
            self.notify(__config__.messages['move_failed_incapacitated'])
            return

        new_room = self.room.directions[direction]
        if not new_room:
            self.notify(__config__.messages['move_failed_no_room'])
            return

        cost = self._get_movement_cost()
        if(self.curmovement >= cost):
            # actor is leaving, subtract movement cost
            self.curmovement -= cost
            self._pre_move(direction)
            self.room = new_room
            self._post_move(room.Direction.get_reverse(direction))
        else:
            self.notify(__config__.messages['move_failed_too_tired'])
    
    def reward_kill(self, victim):
        """Applies kill experience from the victim to the killer and checks
        for a level up.

        """

        # calculate the kill experience
        leveldiff = victim.level - self.level
        experience = 200 + 30 * leveldiff
        if leveldiff > 5:
            experience *= 1 + random.randint(0, leveldiff*2) / 100
        aligndiff = abs(victim.alignment - self.alignment) / 2000
        if aligndiff > 0.5:
            mod = random.randint(15, 35) / 100
            experience *= 1 + aligndiff - mod
        experience = random.uniform(experience * 0.8, experience * 1.2)
        experience = experience if experience > 0 else 0

        # award experience and check for level change
        self.experience += experience
        diff = self.experience / self.experience_per_level
        if diff > self.level:
            gain = 0
            while gain < diff:
                self._level_up()
                gain += 1

    def set_experience_per_level(self):
        """Based on the current configuration of proficiencies, calculate how
        much experience the actor needs to obtain to get a level.

        @todo: stub out this function.
        
        """

        self.experience_per_level = 1000
    
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

        return self.long if self.long else str(self)+" the "+str(self.race)+" is "+self.disposition+" here"

    def add_affect(self, aff):
        """Apply an affect to the actor."""

        try:
            self.dispatch('changed', 
                    affect=aff, actor=self,
                    changed=aff.messages['success']['*'] % self)
        except KeyError:
            pass

        self.affects.append(aff)

        # for any modifiers that are percents, we need to 
        # get the percent of the actor's attribute
        for attr in vars(aff.attributes):
            modifier = getattr(aff.attributes, attr)
            if modifier > 0 and modifier < 1:
                setattr(aff.attributes, attr, self.get_attribute(attr)
                        * modifier)

        if aff.timeout > -1:
            server.__instance__.heartbeat.attach('tick', aff.countdown_timeout)
            aff.attach('end', self._end_affect)

    def leaving(self, _args):
        """Called when an actor leaves a room."""

        pass

    def arriving(self, _args):
        """Called when an actor enters a new room."""

        pass

    def set_target(self, target = None):
        """Sets up a new target for the actor."""

        if not target:
            self.target.detach('attack_resolution', self._normalize_stats)
            self.target = None
            return True

        if self.target:
            self.notify(__config__.messages['target_already_acquired'])
            return False
        
        # target acquired
        self.target = target

        # handles above 100% hp/mana/mv and below 0% hp/mana/mv
        self.target.attach('attack_resolution', self._normalize_stats)

        # calls attack rounds until target is removed
        server.__instance__.heartbeat.attach('pulse', self._do_regular_attacks)
        return True

    def can_see(self):
        """Can the user see?"""

        if utility.match_partial("glow", self.get_affects()):
            return True

        if self.room.get_area().location == room.__LOCATION_OUTSIDE__ and \
                calendar.__instance__.daylight:
            return True

        return self.room.lit

    def is_updateable(self):
        return True

    def get_affects(self):
        """Returns all affects currently applied to the actor, including base
        affects and affects from equipment.

        """

        affects = list(self.affects)
        for _pos, equipment in self.equipped.iteritems():
            if equipment:
                affects += equipment.affects
        return affects

    def _end_affect(self, args):
        """Called when an affect ends."""

        server.__instance__.heartbeat.detach('tick',
                                args['affect'].countdown_timeout)
        self.affects.remove(args['affect'])
        try:
            self.dispatch('changed', 
                    affect=args['affect'], actor=self,
                    changed=args['affect'].messages['end']['*'] % self)
        except KeyError:
            pass
    
    def _tick(self):
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
                self.get_trained_attribute(attribute_name) + \
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
            server.__instance__.heartbeat.detach('pulse', self._do_regular_attacks)

    def _pre_move(self, direction):
        """Called before an actor moves."""

        self.detach('changed', self.room.actor_changed)
        self.room.actor_leave(self, direction)

    def _post_move(self, direction):
        """Called after an actor moves."""

        self.attach('changed', self.room.actor_changed)
        self.room.actor_arrive(self, direction)

    def _level_up(self):
        """Increase the actor's level."""

        self.level += 1
    
    def _end_battle(self):
        """Ensure the actor is removed from battle, unless multiple actors are
        targeting this actor.

        """

        if self.target:
            if self.target.target is self:
                self.target.target = None
            self.target = None
    
    def _die(self):
        """What happens when the user is killed (regardless of the method of
        death). Does basic things such as creating the corpse and dispatching
        a disposition change event.
        
        """

        if self.target:
            self.target.reward_kill(self)
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
        self.room.inventory.append(corpse)
        self.dispatch(
                "changed", 
                actor=self, 
                changed=str(self).title()+" dies.")

    def _command_north(self, _invoked_command, _args):
        """Attempt to move the actor in the north direction."""
        self.move("north")

    def _command_south(self, _invoked_command, _args):
        """Attempt to move the actor in the south direction."""
        self.move("south")

    def _command_east(self, _invoked_command, _args):
        """Attempt to move the actor in the east direction."""
        self.move("east")

    def _command_west(self, _invoked_command, _args):
        """Attempt to move the actor in the west direction."""
        self.move("west")

    def _command_up(self, _invoked_command, _args):
        """Attempt to move the actor in the up direction."""
        self.move("up")

    def _command_down(self, _invoked_command, _args):
        """Attempt to move the actor in the down direction."""
        self.move("down")

    def _command_sit(self, invoked_command, _args):
        """Change the actor's disposition to sitting."""

        self.disposition = Disposition.SITTING
        self.dispatch(
                "changed", 
                actor=self, 
                changed=invoked_command.messages['sit_room'] % (str(self).title()))

    def _command_wake(self, invoked_command, _args):
        """Change the actor's disposition to standing."""

        self.disposition = Disposition.STANDING
        self.dispatch(
                "changed", 
                actor=self, 
                changed=invoked_command.messages['wake_room'] % (str(self).title()))

    def _command_sleep(self, invoked_command, _args):
        """Change the actor's disposition to sleeping."""

        self.disposition = Disposition.SLEEPING
        self.dispatch(
                "changed", 
                actor=self, 
                changed=invoked_command.messages['sleep_room'] % (str(self).title()))

    def _command_wear(self, _invoked_command, _args):
        """Attempt to wear a piece of equipment or a weapon from the inventory.
        
        equipment = utility.match_partial(args[1], self.inventory.items)
        if equipment:
            current_eq = self.get_equipment_by_position(equipment.position)
            if current_eq:
                self._command_remove(['remove', current_eq.name])
            if self.set_equipment(equipment):
                self.notify(invoked_command.messages['success'] % (equipment))
                self.inventory.remove(equipment)
            else:
                self.notify(invoked_command.messages['not_qualified'] % (equipment))
        else:
            self.notify(invoked_command.messages['no_item'])
        """
        self.notify("This is disabled for reworking")
        return
    
    def _command_remove(self, invoked_command, args):
        """Attempt to remove a worn piece of equipment or weapon."""

        equipment = utility.match_partial(args[1], 
            list(eq for eq in self.equipped.values() if eq))
        if equipment:
            self._set_equipment_by_position(equipment.position, None)
            self.notify(invoked_command.messages['success'])
            self.inventory.append(equipment)
        else:
            self.notify(invoked_command.messages['no_item'])

    def _command_kill(self, invoked_command, args):
        """Attempt to kill another actor within the same room."""

        target = utility.match_partial(args[1], self.room.actors)
        if target and self.set_target(target):
            self.room.announce({
                self: invoked_command.messages['success_self'],
                '*': invoked_command.messages['success_room'] % (self, target)
            })
        elif not target:
            self.notify(invoked_command.messages['target_not_found'])

    def _command_flee(self, invoked_command, _args):
        """Attempt to flee from a battle. This will cause the actor to flee
        to another room in a random direction.

        """

        if self.target:
            self._end_battle()
            self.room.announce({
                self: invoked_command.messages['success_self'],
                "*": invoked_command.messages['success_room'] % (str(self).title())
            })
            self.move()
        else:
            self.notify(invoked_command.messages['no_target'])

    def _command_get(self, invoked_command, args):
        """Locates and transfers an item from an accessible inventory into
        the actor's inventory. An accessible inventory is the room's inventory
        or the inventory of a container in the room or in the actor's
        inventory.

        """

        _item = utility.match_partial(args[1], self.room.inventory.items)
        if _item and _item.can_own:
            self.room.inventory.remove(_item)
            self.inventory.append(_item)
            self.room.announce({
                self: invoked_command.messages['success_self'],
                "*": invoked_command.messages['success_room'] % (str(self).title(), _item)
            })
        else:
            if _item:
                self.notify(invoked_command.messages['cannot_own'] % (_item))
            else:
                self.notify(invoked_command.messages['no_item'])

    def _command_drop(self, invoked_command, args):
        """Removes an item from the actor's inventory and adds it to the room
        inventory.

        """

        _item = utility.match_partial(args[1], self.inventory.items)
        if _item:
            self.inventory.remove(_item)
            self.room.inventory.append(_item)
            self.room.announce({
                self: invoked_command.messages['success_self'],
                "*": invoked_command.messages['success_room'] % (str(self).title(), _item)
            })
        else:
            self.notify(invoked_command.messages['no_item'])

class Mob(Actor):
    """NPCs of the game, mobs are the inhabitants of the mud world."""

    ROLE_TRAINER = 'trainer'
    ROLE_ACOLYTE = 'acolyte'

    yaml_tag = "u!mob"

    def __init__(self):
        self.movement = 0
        self.movement_timer = self.movement
        self.respawn = 1
        self.auto_flee = False
        self.area = None
        self.role = ''
        super(Mob, self).__init__()
    
    def _decrement_movement_timer(self):
        """Counts down to 0, at which point the mob will attempt to move from
        their current room to a new one. They cannot move to new areas however.

        """

        self.movement_timer -= 1
        if self.movement_timer < 0:
            direction = random.choice([direction for direction, _room in 
                self.room.directions.iteritems() if _room and 
                _room.area == self.room.area])
            self.move(direction)
            self.movement_timer = self.movement
    
    def _tick(self):
        super(Mob, self)._tick()
        if self.movement:
            self._decrement_movement_timer()
    
    def _normalize_stats(self, _args = None):
        if self.curhp < 0:
            self._die()
        super(Mob, self)._normalize_stats()
    
    def _die(self):
        super(Mob, self)._die()
        self._pre_move("sky")
        self.room = room.__ROOMS__[room.__PURGATORY__]
        self._post_move("sky")
    
class User(Actor):
    """The actor controlled by a client connected by the server."""

    def __init__(self):
        self.delay_counter = 0
        self.last_delay = 0
        self.trains = 5
        self.practices = 5
        self.client = None
        self.observers = {}
        super(User, self).__init__()

    def is_updateable(self):
        return False
    
    def prompt(self):
        """The status prompt for a user. By default, shows current hp, mana,
        and movement. Not yet configurable."""

        return "%i %i %i >> " % (self.curhp, self.curmana, self.curmovement)
    
    def notify(self, message = "", add_prompt = True):
        super(User, self).notify(message, add_prompt)
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
        self.notify(aff.messages['success']['self'])

    def _end_affect(self, args):
        super(User, self)._end_affect(args)
        self.notify(args['affect'].messages['end']['self'])
    
    def _tick(self):
        super(User, self)._tick()
        self.notify()
    
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
        self.room.actor_leave(self)
        self.room = room.__ROOMS__[room.__START_ROOM__]
        self.room.actor_arrive(self)
        self.notify(__config__.messages['died'])
    
    def _update_delay(self):
        """Removes the client from polling for input if the user has a delay
        applied to it.

        """

        if self.delay_counter > 0:
            if not self.last_delay:
                server.__instance__.heartbeat.detach('cycle', self.client.poll)
            currenttime = int(time.time())
            if currenttime > self.last_delay:
                self.delay_counter -= 1
                self.last_delay = currenttime
        elif self.last_delay:
            server.__instance__.heartbeat.attach('cycle', self.client.poll)
            self.last_delay = 0
    
    def _level_up(self):
        super(User, self)._level_up()
        self.notify(__config__.messages['level_up'])

    def perform_ability(self, ability):
        """Applies delay to the user when performing an ability."""
        self.delay_counter += ability.delay+1

    def loggedin(self):
        """Miscellaneous setup tasks for when a user logs in. Nothing too
        exciting.

        """

        # attach server events
        server.__instance__.heartbeat.attach('stat', self.stat)
        server.__instance__.heartbeat.attach('cycle', self._update_delay)

        # set the room
        if self.room_id:
            new_room_id = self.room_id
        else:
            new_room_id = 'room.1'#room.__START_ROOM__
        self.room = room.get(new_room_id)
        self._post_move("sky")

        # listener for client input
        self.client.attach('input', self.check_input)

        # listener for the server tick
        server.__instance__.heartbeat.attach('tick', self._tick)

        # listeners for calendar events (sunrise, sunset) 
        calendar.__instance__.setup_listeners_for(self.calendar_changed)

        # attach listeners to client input for abilities
        """
        for ability in self.get_abilities():
            ability.attach('perform', self.perform_ability)
            if ability.hook == 'input':
                def check_input(args):
                    ""Checks if the user is trying to perform an ability with
                    a given input.

                    ""

                    if ability.name.startswith(args['args'][0]):
                        ability.try_perform(self, args['args'][:2])
                        return True
                self.client.attach('input', check_input)
        """

        debug.log('client logged in as '+str(self))

    def calendar_changed(self, args):
        """Notifies the user when a calendar event happens, such as the sun
        rises.

        """

        self.notify(args['changed'])

    def check_input(self, args):
        """Takes input from the user and tries to find a match against known
        commands.

        """

        args = args['args']

        try:
            com = wireframe.create(args[0])
        except KeyError:
            return False

        if com.required_dispositions and self.disposition not in \
                com.required_dispositions:
            self.notify("You are incapacitated and cannot do that." \
                if self.disposition == Disposition.INCAPACITATED \
                else "You need to be "+(" or ".join(com.required_dispositions))+" to do that.")
        else:
            try:
                getattr(self, "_command_"+com.name)(com, args)
            except AttributeError as e:
                debug.log(e, "notice")
        return True

    def leaving(self, args):
        super(User, self).leaving(args)
        if not args['actor'] == self and args['direction']:
            if self.can_see():
                actor_seen = args['actor']
            else:
                actor_seen = "Someone"
            self.notify(__config__.messages['actor_leaves_room'] % (actor_seen, args['direction']))

    def arriving(self, args):
        super(User, self).arriving(args)
        if args['direction']:
            if self.can_see():
                actor_seen = args['actor']
            else:
                actor_seen = "Someone"
            self.notify(__config__.messages['actor_enters_room'] % (actor_seen, args['direction']))

    def _pre_move(self, direction):
        super(User, self)._pre_move(direction)
        self.room.detach('update', self._room_update)

    def _post_move(self, direction):
        super(User, self)._post_move(direction)
        self._command_look()
        self.room.attach('update', self._room_update)

    def _room_update(self, args):
        """Event listener for when the room update fires."""

        if args['actor'] != self:
            self.notify(args['changed'])

    def save(self):
        """Persists the user as a pickle dump."""

        client = self.client
        _room = self.room
        self.client = None
        self.room = None
        with open(User.get_save_file(self.name), 'wb') as fp:
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)
        self.client = client
        self.room = _room

    @staticmethod
    def get_save_file(name):
        """The path to the user file based on the name given."""

        return os.path.join(os.getcwd(), __SAVE_DIR__, name+'.pk')

    @staticmethod
    def load(name):
        """Attempts to load a user from the user save file. If the file does
        not exist, the client is trying to create a new user.

        """

        user = None
        user_file = User.get_save_file(name)
        if os.path.isfile(user_file):
            with open(user_file, 'rb') as fp:
                user = pickle.load(fp)
        return user

    @staticmethod
    def is_valid_name(name):
        """Check if a user name is a valid format."""

        name_len = len(name)
        return name.isalpha() and name_len > 2 and name_len < 12

    def _command_look(self, _invoked_command = None, args = None):
        """Describes the room and its inhabitants to the user, including
        actors, items on the ground, and the exits.

        """

        args = args or []
        if len(args) <= 1:
            # room and exits
            can_see = self.can_see()
            if can_see:
                msg = "%s\n%s\n" % (self.room.title, self.room.description)
            else:
                msg = __config__.messages["cannot_see_too_dark"]
            msg += "\n[Exits %s]\n" % (
                    "".join(direction[:1] for direction, room in 
                        self.room.directions.iteritems() if room))
            # items
            #msg += self.room.inventory.inspection(' is here.')
            # actors
            if self.room.actors:
                if can_see:
                    msg += "\n".join(_actor.looked_at().capitalize() for _actor
                                in self.room.actors if _actor is not self)+"\n"
                else:
                    msg += \
                    __config__.messages["cannot_see_actors_in_room"]+"\n"
        else:
            looking_at = utility.match_partial(
                    args[0], 
                    self.inventory.items, 
                    self.room.inventory.items, 
                    self.room.actors)
            if looking_at:
                msg = looking_at.description.capitalize()
            else:
                msg = __config__.messages['look_at_nothing']
        self.notify(msg+"\n")

    def _command_affects(self, _invoked_command, _args):
        """Describes the affects currently active on the user."""

        self.notify("Your affects:\n"+"\n".join(str(x)+": "+str(x.timeout)+\
                    " ticks" for x in self.affects))

    def _command_sit(self, invoked_command, args):
        super(User, self)._command_sit(invoked_command, args)
        self.notify(invoked_command.messages['sit_self'])

    def _command_wake(self, invoked_command, args):
        super(User, self)._command_wake(invoked_command, args)
        self.notify(invoked_command.messages['wake_self'])

    def _command_sleep(self, invoked_command, args):
        super(User, self)._command_sleep(invoked_command, args)
        self.notify(invoked_command.messages['sleep_self'])

    def _command_practice(self, invoked_command, args):
        """Describes proficiency information to the user and if an acolyte is
        present, allows the user to get better at those proficiencies.

        """

        if len(args) == 1:
            self.notify("Your proficiencies:\n" + \
                    "\n".join(name+": "+str(proficiency.level) \
                    for name, proficiency in 
                        self._get_proficiencies().iteritems()))
        elif any(mob.role == Mob.ROLE_ACOLYTE for mob in self.room.mobs()):
            for prof_name, prof in self._get_proficiencies().iteritems():
                if prof_name.find(args[1]) == 0:
                    if self.practices:
                        self.practices -= 1
                        prof.level += 1
                        self.room.announce({
                            self: invoked_command.messages['success_self'] % (prof_name),
                            '*': invoked_command.messages['success_room'] % (str(self).title(), prof_name)
                        })
                    else:
                        self.notify(invoked_command.messages['no_practices'])
                    return
                self.notify(invoked_command.messages['not_proficiency'])
        else:
            self.notify(invoked_command.messages['no_acolyte'])

    def _command_quit(self, _invoked_command, _args):
        """Saves and disconnects the user."""

        self.save()
        self.client.disconnect()

    def _command_equipped(self, _invoked_command, _args):
        """Tells the user what they have equipped."""

        msg = ""
        for position, equipment in self.equipped.iteritems():
            msg += re.sub(r"\d+", "", position)+": "+str(equipment)+"\n"
        self.notify("You are wearing: "+msg)

    def _command_score(self, _invoked_command, _args):
        """Provides a more detailed score card of the user's status, including
        name, race, attributes, carrying weight, trains, practices, and
        experience.

        """

        self.notify(("You are %s, a %s\n"+\
            "%i/%i hp %i/%i mana %i/%i mv\n"+\
            "str (%i/%i), int (%i/%i), wis (%i/%i), dex (%i/%i), con(%i/%i),"+\
            "cha(%i/%i)\nYou are carrying %g/%i lbs\n"+\
            "You have %i trains, %i practices\n"+\
            "You are level %i with %i experience, %i to next level\n"+\
            "Your alignment is: %s") % (self, self.race, self.curhp, 
            self.get_attribute('hp'), self.curmana,
            self.get_attribute('mana'), self.curmovement,
            self.get_attribute('movement'),
            self.get_attribute('str'), self._get_unmodified_attribute('str'),
            self.get_attribute('int'), self._get_unmodified_attribute('int'),
            self.get_attribute('wis'), self._get_unmodified_attribute('wis'),
            self.get_attribute('dex'), self._get_unmodified_attribute('dex'),
            self.get_attribute('con'), self._get_unmodified_attribute('con'),
            self.get_attribute('cha'), self._get_unmodified_attribute('cha'),
            self.inventory.get_weight(), self._get_max_weight(),
            self.trains, self.practices, self.level, self.experience,
            (self.experience % self.experience_per_level),
            self.get_alignment()))

    def _command_inventory(self, _invoked_command, _args):
        """Relays the user's inventory of items back to them."""

        self.notify("Your inventory:\n"+str(self.inventory))

    def _command_who(self, invoked_command, args):
        """
        wholist = ''
        for i in self.client.factory.clients:
            wholist += str(i.user) if i.user else ""
        l = len(self.client.factory.clients)
        wholist += "\n"+str(l)+" player"+("" if l == 1 else "s")+" found."
        self.notify(wholist)
        """
        pass

    def _command_train(self, invoked_command, args):
        """Handles training the user and displaying information about what
        attributes may still be trained. Requires a trainer in the room.

        """

        if self.trains < 1:
            self.notify(invoked_command.messages['no_trains'])
            return
        if not any(mob.role == Mob.ROLE_TRAINER for mob in self.room.mobs()):
            self.notify(invoked_command.messages['no_trainers'])
            return
        if len(args) == 0:
            message = ""
            for stat in Actor.stats:
                attr = self.get_attribute(stat)
                mattr = self.get_max_attribute(stat)
                if attr+1 <= mattr:
                    message += stat+" "
            self.notify("You can train: "+message)
            return
        stat = args[0]
        if stat in Actor.stats:
            attr = self.get_attribute(stat)
            mattr = self.get_max_attribute(stat)
            if attr+1 <= mattr:
                setattr(self.trained_attributes, stat, getattr(self.trained_attributes, stat)+1)
                self.trains -= 1
                self.room.announce({
                    self: invoked_command.messages['success_self'] % (stat),
                    '*': invoked_command.messages['success_room'] % (str(self).title(), stat)
                })
            else:
                self.notify(invoked_command.messages['maxed_stat'] % (stat))
        else:
            self.notify(invoked_command.messages['not_trainable'])

    def _command_date(self, _command, _args):
        """Notifies the user of the in-game date and time."""

        self.notify(calendar.__instance__)

    def _command_time(self, _command, _args):
        """Notifies the user of the in-game date and time."""

        self.notify(calendar.__instance__)

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

        self.aggressor.dispatch('attackstart', attack=self)

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

        self.aggressor.dispatch('attackmodifier', attack=self)

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
        aggressor.room.announce({
            aggressor: "("+attackname+") Your "+verb+" attack "+is_hit+" "+tarname+".",
            aggressor.target: ucname+"'s "+verb+" attack "+is_hit+" you.",
            "*": ucname+"'s "+verb+" attack "+is_hit+" "+tarname+"."
        }, add_prompt = False)

        #need to do this check again here, can't have the actor dead before the hit message
        if roll > 0: 
            aggressor.target.curhp -= dam_roll

        aggressor.dispatch('attack_resolution', attack=self)

class Ability(observer.Observer, room.Reporter):
    """Represents something cool an actor can do. Invoked when the hook is
    triggered on the parent actor. Applies costs in the costs dict, and affects
    in the affects list.
    
    """

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
        super(Ability, self).__init__()
    
    def try_perform(self, invoker, args):
        """Parses the user input, finds a target, applies the ability cost,
        and invokes the ability.

        """

        args = args[0]
        try:
            receiver = utility.match_partial(args[-1], invoker.room.actors)
        except IndexError:
            receiver = invoker
        if not receiver:
            receiver = invoker
        if self.apply_cost(invoker):
            invoker.delay_counter += self.delay + 1
            success = random.randint(0, 1)
            if success:
                self.perform(receiver)
            else:
                receiver.room.announce(self.get_messages('fail', invoker, receiver))
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

class Race(yaml.YAMLObject):
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
        try:
            return self.attributes[attribute]
        except KeyError:
            return 0
    
    def add_proficiency(self, prof, level):
        """Give a proficiency to this race. Actor's proficiencies are a
        composite of what they know and the race they are assigned.

        """

        prof = str(prof)
        try:
            self.proficiencies[prof].level += level
        except KeyError:
            self.proficiencies[prof] = wireframe.create(prof)
            self.proficiencies[prof].level = level

    def __str__(self):
        return self.name
