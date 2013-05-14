from . import debug, utility

def train(actor, args):
    if actor.trains < 1:
        actor.notify("You don't have any trains.")
        return
    hasTrainer = False
    from actor import Mob
    if not any(mob.role == Mob.ROLE_TRAINER for mob in actor.room.mobs()):
        actor.notify("There are no trainers here.")
        return
    from attributes import Attributes
    if len(args) == 0:
        message = ""
        for stat in Attributes.stats:
            attr = actor.getAttribute(stat)
            mattr = actor.getMaxAttribute(stat)
            if attr+1 <= mattr:
                message += stat+" "
        actor.notify("You can train: "+message)
        return
    stat = args[0]
    if stat in Attributes.stats:
        attr = actor.getAttribute(stat)
        mattr = actor.getMaxAttribute(stat)
        if attr+1 <= mattr:
            setattr(actor.trainedAttributes, stat, getattr(actor.trainedAttributes, stat)+1)
            actor.trains -= 1
            actor.notify("Your "+stat+" increases!")
        else:
            actor.notify("You cannot train "+stat+" any further.")
    else:
        actor.notify("You cannot train that.")

def wear(actor, args):
    equipment = utility.match_partial(args[0], actor.inventory.items)
    if equipment:
        currentEq = actor.getEquipmentByPosition(equipment.position)
        if currentEq:
            Remove().perform(actor, [currentEq.name])
        if actor.setEquipment(equipment):
            actor.notify("You wear "+str(equipment)+".")
            actor.inventory.remove(equipment)
        else:
            actor.notify("You are not qualified enough to equip "+str(equipment)+".")
    else:
        actor.notify("You have nothing like that.")

def remove(actor, args):
    equipment = utility.match_partial(args[0], list(equipment for equipment in actor.equipped.values() if equipment))
    if equipment:
        actor.setEquipmentByPosition(equipment.position, None)
        actor.notify("You remove "+str(equipment)+" and place it in your inventory.")
        actor.inventory.append(equipment)
    else:
        actor.notify("You are not wearing that.")

def equipped(actor, args):
    import re
    msg = ""
    for p, e in actor.equipped.iteritems():
        msg += re.sub("\d+", "", p)+": "+str(e)+"\n"
    actor.notify("You are wearing: "+msg)

def sleep(actor, args):
    from . import actor
    actor.disposition = actor.Disposition.SLEEPING
    actor.room.dispatch("disposition_changed", actor=actor, changed=str(actor).title()+" goes to sleep.")
    actor.notify("You go to sleep.")

def kill(actor, args):
    target = utility.match_partial(args[0], actor.room.actors)
    if target:
        actor.target = target
        import server
        server.__instance__.heartbeat.attach('pulse', actor.pulse)
        actor.room.announce({
            actor: 'You scream and attack!',
            '*': str(actor)+' screams and attacks '+str(target)+'!'
        })
    else:
        actor.notify("They aren't here.")

def flee(actor, args):
    if actor.target:
        actor.removeFromBattle()
        actor.room.announce({
            actor: "You run scared!",
            "*": str(actor).title()+" runs scared!"
        })
        actor.move()
    else:
        actor.notify("You're not fighting anyone!")

def get(actor, args):
    item = utility.match_partial(args[0], actor.room.inventory.items)
    if item and item.can_own:
        actor.room.inventory.remove(item)
        actor.inventory.append(item)
        actor.notify("You pick up "+str(item)+" off the floor.")
    else:
        actor.notify("Nothing is there." if not item else "You cannot pick up "+str(item)+".")

def drop(actor, args):
    item = utility.match_partial(args[0], actor.inventory.items)
    if item:
        actor.inventory.remove(item)
        actor.room.inventory.append(item)
        actor.notify("You drop "+str(item)+" to the floor.")
    else:
        actor.notify("Nothing is there.")

def inventory(actor, args):
    actor.notify("Your inventory:\n"+str(actor.inventory))

def score(actor, args):
    msg = "You are %s, a %s\n%i/%i hp %i/%i mana %i/%i mv\nstr (%i/%i), int (%i/%i), wis (%i/%i), dex (%i/%i), con(%i/%i), cha(%i/%i)\nYou are carrying %g/%i lbs\nYou have %i trains, %i practices\nYou are level %i with %i experience, %i to next level\nYour alignment is: %s" % ( \
        actor, actor.race, actor.curhp, actor.getAttribute('hp'), actor.curmana, \
        actor.getAttribute('mana'), actor.curmovement, actor.getAttribute('movement'), \
        actor.getAttribute('str'), actor.getUnmodifiedAttribute('str'), \
        actor.getAttribute('int'), actor.getUnmodifiedAttribute('int'), \
        actor.getAttribute('wis'), actor.getUnmodifiedAttribute('wis'), \
        actor.getAttribute('dex'), actor.getUnmodifiedAttribute('dex'), \
        actor.getAttribute('con'), actor.getUnmodifiedAttribute('con'), \
        actor.getAttribute('cha'), actor.getUnmodifiedAttribute('cha'), \
        actor.inventory.get_weight(), actor.getMaxWeight(), \
        actor.trains, actor.practices, actor.level, actor.experience, actor.experience % actor.getExperiencePerLevel(), \
        actor.getAlignment())
    actor.notify(msg);

def who(actor, args):
    wholist = '';
    for i in actor.client.factory.clients:
        wholist += str(i.user) if i.user else ""
    l = len(actor.client.factory.clients)
    wholist += "\n"+str(l)+" player"+("" if l == 1 else "s")+" found."
    actor.notify(wholist)

class Command(object):

    def __init__(self):
        self.name = ""
        self.required_dispositions = []

    def try_perform(self, performer, args = []):
        from . import actor
        if self.required_dispositions and performer.disposition \
                                not in self.required_dispositions:
            performer.notify("You are incapacitated and cannot do that." \
                if performer.disposition == actor.Disposition.INCAPACITATED \
                else "You need to be "+(" or ".join(self.required_dispositions))+" to do that.")
        else:
            try:
                getattr(performer, "command_"+self.name)(args)
            except AttributeError as e:
                #debug.log(str(type(performer))+" needs to implement command_"+self.name, "notice")
                debug.log(e, "notice")
    
    def __str__(self):
        return self.name
