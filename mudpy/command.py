from utility import matchPartial, startsWith
from actor import Disposition
import debug

def checkInput(args):
    import factory
    try:
        action = factory.new(Command(), factory.match(args[1], 'Command')['wireframe'])
    except (factory.FactoryException, TypeError) as e:
        return False
    action.tryPerform(args[0], args[2:])
    return True

def practice(actor, args):
    if len(args) == 0:
        actor.notify("Your proficiencies:\n"+"\n".join(name+": "+str(proficiency.level) for name, proficiency in actor.getProficiencies().iteritems()))
    else:
        from actor import Mob
        if not any(mob.role == Mob.ROLE_ACOLYTE for mob in actor.room.mobs()):
            actor.notify("No one is here to help you practice.")
            return;
        proficiency = ""
        for p in actor.getProficiencies():
            if p.find(args[0]) == 0:
                proficiency = p
        if proficiency:
            actor.getProficiency(proficiency).level += 1
            actor.notify("You get better at "+proficiency+"!")
        else:
            actor.notify("You cannot practice that.")

def north(actor, args):
    moveDirection(actor, args, "north")

def south(actor, args):
    moveDirection(actor, args, "south")

def east(actor, args):
    moveDirection(actor, args, "east")

def west(actor, args):
    moveDirection(actor, args, "west")

def up(actor, args):
    moveDirection(actor, args, "up")

def down(actor, args):
    moveDirection(actor, args, "down")

def moveDirection(actor, args, direction):
    if actor.target:
        actor.notify("You are fighting!")
        return

    if actor.disposition == Disposition.INCAPACITATED:
        actor.notify("You are incapacitated and will die soon if not aided.")
        return

    try:
        newRoom = actor.room.directions[direction]
    except KeyError:
        actor.notify("Alas, nothing is there.")
        return

    cost = actor.getMovementCost()
    if(actor.attributes.movement >= cost):
        actor.attributes.movement -= cost
        actor.room.notify(actor, str(actor).capitalize()+" leaves "+direction+".")
        actor.room.actors.remove(actor)
        actor.room = newRoom
        actor.room.actors.append(actor)
        actor.room.notify(actor, str(actor).capitalize()+" has arrived.")
        import factory
        factory.new(Command(), "look").tryPerform(actor)
        debug.log(str(actor)+' moves to '+str(actor.room))
    else:
        actor.notify("You are too tired to move.")

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
    equipment = matchPartial(args[0], actor.inventory.items)
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
    equipment = matchPartial(args[0], list(equipment for equipment in actor.equipped.values() if equipment))
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

def sit(actor, args):
    actor.disposition = Disposition.SITTING
    actor.room.announce({
        actor: "You sit down and rest.",
        "*": str(actor).title()+" sits down and rests."
    })

def sleep(actor, args):
    actor.disposition = Disposition.SLEEPING
    actor.room.announce({
        actor: "You go to sleep.",
        "*": str(actor).title()+" goes to sleep."
    })

def wake(actor, args):
    actor.disposition = Disposition.STANDING
    actor.room.announce({
        actor: "You stand up.",
        "*": str(actor).title()+" stands up."
    })

def kill(actor, args):
    target = matchPartial(args[0], actor.room.actors)
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
    item = matchPartial(args[0], actor.room.inventory.items)
    if item and item.canOwn:
        actor.room.inventory.remove(item)
        actor.inventory.append(item)
        actor.notify("You pick up "+str(item)+" off the floor.")
    else:
        actor.notify("Nothing is there." if not item else "You cannot pick up "+str(item)+".")

def drop(actor, args):
    item = matchPartial(args[0], actor.inventory.items)
    if item:
        actor.inventory.remove(item)
        actor.room.inventory.append(item)
        actor.notify("You drop "+str(item)+" to the floor.")
    else:
        actor.notify("Nothing is there.")

def inventory(actor, args):
    actor.notify("Your inventory:\n"+actor.inventory.inspection())

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
        actor.inventory.getWeight(), actor.getMaxWeight(), \
        actor.trains, actor.practices, actor.level, actor.experience, actor.experience % actor.getExperiencePerLevel(), \
        actor.getAlignment())
    actor.notify(msg);

def look(actor, args):
    if len(args) == 0:
        # room and exits
        msg = "%s\n%s\n\n[Exits %s]\n" % (actor.room.name, actor.room.description, "".join(direction[:1] for direction, room in actor.room.directions.iteritems() if room))
        # items
        msg += actor.room.inventory.inspection(' is here.')
        # actors
        msg += "\n".join(_actor.lookedAt().capitalize() for _actor in actor.room.actors if _actor is not actor)+"\n"
    else:
        lookingAt = matchPartial(args[0], actor.inventory.items, actor.room.inventory.items, actor.room.actors)
        msg = lookingAt.description.capitalize()+"\n" if lookingAt else "Nothing is there."
    actor.notify(msg)

def quit(actor, args):
    actor.client.disconnect()

def who(actor, args):
    wholist = '';
    for i in actor.client.factory.clients:
        wholist += str(i.user) if i.user else ""
    l = len(actor.client.factory.clients)
    wholist += "\n"+str(l)+" player"+("" if l == 1 else "s")+" found."
    actor.notify(wholist)

def affects(actor, args):
    actor.notify("Your affects:\n"+"\n".join(str(x)+": "+str(x.timeout)+" ticks" for x in actor.affects));

class Command(object):

    def __init__(self):
        self.name = ""
        self.requiresStandingDisposition = False

    def tryPerform(self, actor, args = []):
        if self.requiresStandingDisposition and actor.disposition != Disposition.STANDING:
            actor.notify("You are incapacitated and cannot do that." if actor.disposition == Disposition.INCAPACITATED else "You need to be standing to do that.")
        else:
            self.perform(actor, args)

    def perform(self, actor, args):
        try:
            globals()[self.name](actor, args)
        except Exception as e:
            debug.log(e, "error")
    
    def __str__(self):
        return self.name
