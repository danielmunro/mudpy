from . import wireframe
import random

def check_input(user, args):

    command = args[0]
    params = args[1:]

    try:
        command = wireframe.create_from_match("command."+command)
    except wireframe.WireframeException:
        return False

    command.run(user, params)

    return True

def move(actor, direction = None):
    """Try to move the actor in the given direction."""

    from . import room

    if not direction:
        direction = random.choice([direction for direction, _room 
            in actor.get_room().directions.iteritems() if _room])

    actor.curmovement -= actor._get_movement_cost()
    actor.get_room().move_actor(actor, direction)

def look(actor, _args = []):
    _room = actor.get_room()
    if len(_args) <= 1:
        can_see = actor.can_see()
        if can_see:
            msg = "%s\n%s\n" % (_room.title, _room.description)
        else:
            msg = __config__.messages["cannot_see_too_dark"]
        msg += "\n[Exits %s]\n" % (
                "".join(direction[:1] for direction, room in 
                    _room.directions.iteritems() if room))
        if _room.actors:
            if can_see:
                msg += "".join(_actor.looked_at().capitalize()+"\n" for _actor
                            in _room.actors if _actor is not actor)
            else:
                msg += \
                __config__.messages["cannot_see_actors_in_room"]+"\n"
    else:
        from . import collection
        looking_at = collection.find(_args, actor.inventory.items)
        if not looking_at:
            looking_at = collection.find(_args, _room.inventory.items)
        if not looking_at:
            looking_at = _room.get_actor(_args)
        if looking_at:
            msg = looking_at.description
        else:
            msg = __config__.messages['look_at_nothing']
    actor.notify(msg)

def affects(actor):
    """Describes the affects currently active on the user."""

    actor.notify("Your affects:\n"+"\n".join(str(x)+": "+str(x.timeout)+\
                " ticks" for x in actor.affects))

def equipped(user):
    """Tells the user what they have equipped."""
    import re

    msg = ""
    for position, equipment in user.equipped.iteritems():
        msg += re.sub(r"\d+", "", position)+": "+str(equipment)+"\n"
    user.notify("You are wearing: "+msg)

def score(user):
    """Provides a more detailed score card of the user's status, including
    name, race, attributes, carrying weight, trains, practices, and
    experience.

    """

    user.notify(("You are %s, a %s\n"+\
        "%i/%i hp %i/%i mana %i/%i mv\n"+\
        "str (%i/%i), int (%i/%i), wis (%i/%i), dex (%i/%i), con(%i/%i),"+\
        "cha(%i/%i)\nYou are carrying %g/%i lbs\n"+\
        "You have %i trains, %i practices\n"+\
        "You are level %i with %i experience, %i to next level\n"+\
        "Your alignment is: %s") % (user, user.race, user.curhp, 
        user.get_attribute('hp'), user.curmana,
        user.get_attribute('mana'), user.curmovement,
        user.get_attribute('movement'),
        user.get_attribute('str'), user._get_unmodified_attribute('str'),
        user.get_attribute('int'), user._get_unmodified_attribute('int'),
        user.get_attribute('wis'), user._get_unmodified_attribute('wis'),
        user.get_attribute('dex'), user._get_unmodified_attribute('dex'),
        user.get_attribute('con'), user._get_unmodified_attribute('con'),
        user.get_attribute('cha'), user._get_unmodified_attribute('cha'),
        user.inventory.get_weight(), user._get_max_weight(),
        user.trains, user.practices, user.level, user.experience,
        (user.experience % user.experience_per_level),
        user.get_alignment()))

def inventory(user):
    """Relays the user's inventory of items back to them."""

    user.notify("Your inventory:\n"+str(user.inventory))

def who(user):
    wholist = ''
    for i in user.client.client_factory.clients:
        wholist += str(i.user)+"\n" if i.user else ""
    l = len(user.client.client_factory.clients)
    wholist += "\n"+str(l)+" player"+("" if l == 1 else "s")+" found."
    user.notify(wholist)

def date(user):
    """Notifies the user of the in-game date and time."""
    from . import calendar

    user.notify(calendar.__instance__.get_game_time())

def time(user):
    """Notifies the user of the in-game date and time."""
    from . import calendar

    user.notify(calendar.__instance__.get_game_time())

def kill(actor, _target):
    """Attempt to kill another actor within the same room."""

    target = actor.get_room().get_actor(_target)
    if target:
        actor.set_target(target)
        actor.get_room().announce({
            actor: actor.last_command.messages['success_self'],
            'all': actor.last_command.messages['success_room'] % (actor, target)
        })
    elif not target:
        actor.notify(actor.last_command.messages['target_not_found'])

def flee(actor):
    """Attempt to flee from a battle. This will cause the actor to flee
    to another room in a random direction.

    """

    if actor.target:
        actor._end_battle()
        actor.get_room().announce({
            actor: actor.last_command.messages['success_self'],
            'all': actor.last_command.messages['success_room'] % (str(actor).title())
        })
        move(actor)
        look(actor)
    else:
        actor.notify(actor.last_command.messages['no_target'])
"""
def _command_wear(self, _invoked_command, _args):
    ""Attempt to wear a piece of equipment or a weapon from the inventory.
    
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
    ""
    self.notify("This is disabled for reworking")
    return

def _command_remove(self, invoked_command, args):
    ""Attempt to remove a worn piece of equipment or weapon.""

    equipment = utility.match_partial(args[1], 
        list(eq for eq in self.equipped.values() if eq))
    if equipment:
        self._set_equipment_by_position(equipment.position, None)
        self.notify(invoked_command.messages['success'])
        self.inventory.append(equipment)
    else:
        self.notify(invoked_command.messages['no_item'])

def _command_get(self, invoked_command, args):
    ""Locates and transfers an item from an accessible inventory into
    the actor's inventory. An accessible inventory is the room's inventory
    or the inventory of a container in the room or in the actor's
    inventory.

    ""

    _item = utility.match_partial(args[1], self.get_room().inventory.items)
    if _item and _item.can_own:
        self.get_room().inventory.remove(_item)
        self.inventory.append(_item)
        self.get_room().announce({
            self: invoked_command.messages['success_self'],
            "*": invoked_command.messages['success_room'] % (str(self).title(), _item)
        })
    else:
        if _item:
            self.notify(invoked_command.messages['cannot_own'] % (_item))
        else:
            self.notify(invoked_command.messages['no_item'])

def _command_drop(self, invoked_command, args):
    ""Removes an item from the actor's inventory and adds it to the room
    inventory.

    ""

    _item = utility.match_partial(args[1], self.inventory.items)
    if _item:
        self.inventory.remove(_item)
        self.get_room().inventory.append(_item)
        self.get_room().announce({
            self: invoked_command.messages['success_self'],
            "*": invoked_command.messages['success_room'] % (str(self).title(), _item)
        })
    else:
        self.notify(invoked_command.messages['no_item'])

def _command_practice(self, invoked_command, args):
    ""Describes proficiency information to the user and if an acolyte is
    present, allows the user to get better at those proficiencies.

    ""

    _room = self.get_room()

    if len(args) == 1:
        self.notify("Your proficiencies:\n" + \
                "\n".join(name+": "+str(proficiency.level) \
                for name, proficiency in 
                    self._get_proficiencies().iteritems()))
    elif any(mob.role == Mob.ROLE_ACOLYTE for mob in _room.mobs()):
        for prof_name, prof in self._get_proficiencies().iteritems():
            if prof_name.find(args[1]) == 0:
                if self.practices:
                    self.practices -= 1
                    prof.level += 1
                    _room.announce({
                        self: invoked_command.messages['success_self'] % (prof_name),
                        '*': invoked_command.messages['success_room'] % (str(self).title(), prof_name)
                    })
                else:
                    self.notify(invoked_command.messages['no_practices'])
                return
            self.notify(invoked_command.messages['not_proficiency'])
    else:
        self.notify(invoked_command.messages['no_acolyte'])

def _command_train(self, invoked_command, args):
    ""Handles training the user and displaying information about what
    attributes may still be trained. Requires a trainer in the room.

    ""

    if self.trains < 1:
        self.notify(invoked_command.messages['no_trains'])
        return
    if not any(mob.role == Mob.ROLE_TRAINER for mob in self.get_room().mobs()):
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
            self.get_room().announce({
                self: invoked_command.messages['success_self'] % (stat),
                '*': invoked_command.messages['success_room'] % (str(self).title(), stat)
            })
        else:
            self.notify(invoked_command.messages['maxed_stat'] % (stat))
    else:
        self.notify(invoked_command.messages['not_trainable'])
"""

class Command(wireframe.Blueprint):

    yaml_tag = "u!command"

    def __init__(self):
        self.name = ""
        self.action = ""
        self.required = []
        self.messages = {}
        self.dispatches = {}
        self.execute = []

    def run(self, actor, args):
        """Takes an actor and input arguments and runs the command."""

        handled = self.required_chain(actor)
        if handled:
            return

        self.execute_chain(actor, args)

    def execute_chain(self, actor, args):
        if actor.can(self.action):
            actor.last_command = self
            handled = self.dispatch_chain(actor)
            if handled:
                return
            for e in self.execute:
                eval(e)

    def required_chain(self, actor):
        for req in self.required:
            req_value = req['value'] if 'value' in req else True
            if 'property' in req:
                req_prop = req['property']
                attr = getattr(actor, req_prop)
                if (req_value is True and not attr) or (not isinstance(req_value, bool) and not attr in req_value):
                #if req_value is True and not attr or not attr in req_value:
                    self.fail(actor, req_value, req['fail'] if 'fail' in req else '')
                    return True
            elif 'method' in req:
                req_method = req['method']
                attr = getattr(actor, req_method)
                if not attr() == req_value:
                    self.fail(actor, req_value, req['fail'] if 'fail' in req else '')
                    return True
    
    def dispatch_chain(self, actor):
        for d in self.dispatches:
            call = d['object']+".dispatch('"+d['event']+"', actor)"
            handled = eval(call)
            if handled:
                return True

    def fail(self, actor, req_value, fail):
        if '%s' in fail:
            if isinstance(req_value, list):
                fail_val = " or ".join(req_value)
            else:
                fail_val = req_value
            actor.notify((fail+"\n") % fail_val)
        elif fail:
            actor.notify(fail+"\n")
    
    def __str__(self):
        return self.name
