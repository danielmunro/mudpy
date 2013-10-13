from . import wireframe
import random

def check_input(event):
    args = event['args']
    user = event['user']

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
            in curroom.directions.iteritems() if _room])

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
        from . import utility
        looking_at = utility.match_partial(
                _args, 
                actor.inventory.items, 
                _room.inventory.items, 
                _room.actors)
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
            req_value = req['value']
            if 'property' in req:
                req_prop = req['property']
                attr = getattr(actor, req_prop)
                if not attr in req_value:
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
            call = d['object']+".dispatch('"+d['event']+"', actor=actor)"
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
