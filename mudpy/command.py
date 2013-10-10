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

    return command.run(user, params)

def level(actor):
    if actor.qualifies_for_level():
        actor.level_up()

def move(actor, direction = None):
    """Try to move the actor in the given direction."""

    from . import room

    if not direction:
        direction = random.choice([direction for direction, _room 
            in actor.get_room().directions.iteritems() if _room])

    new_room = actor.get_room().directions[direction]
    actor.curmovement -= actor._get_movement_cost()
    actor._pre_move(direction)
    actor.room = new_room
    actor._post_move(room.Direction.get_reverse(direction))

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
        looking_at = utility.match_partial(
                _args[0], 
                actor.inventory.items, 
                _room.inventory.items, 
                _room.actors)
        if looking_at:
            msg = looking_at.description.capitalize()
        else:
            msg = __config__.messages['look_at_nothing']
    actor.notify(msg)

def affects(actor):
    """Describes the affects currently active on the user."""

    actor.notify("Your affects:\n"+"\n".join(str(x)+": "+str(x.timeout)+\
                " ticks" for x in actor.affects))

class Command(wireframe.Blueprint):

    yaml_tag = "u!command"

    def __init__(self):
        self.name = ""
        self.required = []
        self.messages = {}
        self.execute = []

    def run(self, actor, args):
        """Takes an actor and input arguments and runs the command."""

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

        for chain in self.execute:
            _args = chain['args'] if 'args' in chain else args
            actor.last_action = chain['method']
            actor.last_args = _args
            handled = actor.dispatch('action')
            if handled:
                return True
            method = chain['method']
            globals()[method](actor, *_args)

        return True
    
    def fail(self, actor, req_value, fail):
        if '%s' in fail:
            if isinstance(req_value, list):
                fail_val = " or ".join(req_value)
            else:
                fail_val = req_value
            actor.notify((fail+"\n") % fail_val)
        else:
            actor.notify(fail+"\n")
    
    def __str__(self):
        return self.name
