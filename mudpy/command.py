from utility import *
from actor import Disposition

class Command(object):
	name = ""
	requiresStandingDisposition = False
	def tryPerform(self, actor, args = []):
		if self.requiresStandingDisposition and actor.disposition != Disposition.STANDING:
			msg = "You are incapacitated and cannot do that." if actor.disposition == Disposition.INCAPACITATED else "You need to be standing to do that."
			actor.notify(msg)
			return
		else:
			self.perform(actor, args)

	def perform(self):
		print "perform() not defined"
		raise
	
	def __str__(self):
		return self.name

class CommandPractice(Command):
	name = "practice"
	def perform(self, actor, args = []):
		actor.notify("Your proficiencies:\n"+"\n".join(proficiency+": "+str(actor.getProficiencyIn(proficiency)) for proficiency in actor.proficiencies))

class CommandTrain(Command):
	name = "train"
	def perform(self, actor, args = []):
		if actor.trains < 1:
			actor.notify("You don't have any trains.")
			return
		hasTrainer = False
		from actor import Mob
		for mob in actor.room.mobs():
			if mob.role == Mob.ROLE_TRAINER:
				hasTrainer = True
				break
		if not hasTrainer:
			actor.notify("There are no trainers here.")
			return
		from attributes import Attributes
		stat = args[1]
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

class CommandWear(Command):
	name = "wear"
	def perform(self, actor, args = []):
		equipment = matchPartial(args[1], actor.inventory.items)
		if equipment:
			currentEq = actor.getEquipmentByPosition(equipment.position)
			if currentEq:
				CommandRemove().perform(actor, [currentEq.name])
			if actor.setEquipment(equipment):
				actor.notify("You wear "+str(equipment)+".")
				actor.inventory.remove(equipment)
			else:
				actor.notify("You are not qualified enough to equip "+str(equipment)+".")
		else:
			actor.notify("You have nothing like that.")

class CommandRemove(Command):
	name = "remove"
	def perform(self, actor, args = []):
		equipment = matchPartial(args[1], list(equipment for equipment in actor.equipped.values() if equipment))
		if equipment:
			actor.setEquipmentByPosition(equipment.position, None)
			actor.notify("You remove "+str(equipment)+" and place it in your inventory.")
			actor.inventory.append(equipment)
		else:
			actor.notify("You are not wearing that.")

class CommandEquipped(Command):
	name = "equipped"
	def perform(self, actor, args = []):
		import re
		msg = ""
		for p, e in actor.equipped.iteritems():
			msg += re.sub("\d+", "", p)+": "+str(e)+"\n"
		actor.notify("You are wearing: "+msg)

class CommandSit(Command):
	name = "sit"
	def perform(self, actor, args = []):
		actor.disposition = Disposition.SITTING
		actor.room.announce({
			actor: "You sit down and rest.",
			"*": str(actor).title()+" sits down and rests."
		})

class CommandSleep(Command):
	name = "sleep"
	def perform(self, actor, args = []):
		actor.disposition = Disposition.SLEEPING
		actor.room.announce({
			actor: "You go to sleep.",
			"*": str(actor).title()+" goes to sleep."
		})

class CommandWake(Command):
	name = "wake"
	def perform(self, actor, args = []):
		actor.disposition = Disposition.STANDING
		actor.room.announce({
			actor: "You stand up.",
			"*": str(actor).title()+" stands up."
		})

class CommandKill(Command):
	name = "kill"
	requiresStandingDisposition = True
	def perform(self, actor, args = []):
		target = matchPartial(args[1], actor.room.actors)
		if target:
			actor.target = target
			from heartbeat import Heartbeat
			Heartbeat.instance.attach('pulse', actor)
		else:
			actor.notify("They aren't here.")

class CommandFlee(Command):
	name = "flee"
	requiresStandingDisposition = True
	def perform(self, actor, args = []):
		if actor.target:
			actor.removeFromBattle()
			actor.room.announce({
				actor: "You run scared!",
				"*": str(actor).title()+" runs scared!"
			})
			actor.move()
		else:
			actor.notify("You're not fighting anyone!")

class CommandGet(Command):
	name = "get"
	requiresStandingDisposition = True
	def perform(self, actor, args = []):
		item = matchPartial(args[1], actor.room.inventory.items)
		if item and item.canOwn:
			actor.room.inventory.remove(item)
			actor.inventory.append(item)
			actor.notify("You pick up "+str(item)+" off the floor.")
		else:
			actor.notify("Nothing is there." if not item else "You cannot pick up "+str(item)+".")

class CommandDrop(Command):
	name = "drop"
	requiresStandingDisposition = True
	def perform(self, actor, args = []):
		item = matchPartial(args[1], actor.inventory.items)
		if item:
			actor.inventory.remove(item)
			actor.room.inventory.append(item)
			actor.notify("You drop "+str(item)+" to the floor.")
		else:
			actor.notify("Nothing is there.")

class CommandInventory(Command):
	name = "inventory"
	def perform(self, actor, args = []):
		actor.notify("Your inventory:\n"+actor.inventory.inspection())

class CommandScore(Command):
	name = "score"
	def perform(self, actor, args = []):
		msg = "You are %s, a %s\n%i/%i hp %i/%i mana %i/%i mv\nstr (%i/%i), int (%i/%i), wis (%i/%i), dex (%i/%i), con(%i/%i), cha(%i/%i)\nYou are carrying %g/%i lbs\nYou have %i trains, %i practices" % ( \
			actor, actor.race, actor.getAttribute('hp'), actor.getMaxAttribute('hp'), actor.getAttribute('mana'), \
			actor.getMaxAttribute('mana'), actor.getAttribute('movement'), actor.getMaxAttribute('movement'), \
			actor.getAttribute('str'), actor.getUnmodifiedAttribute('str'), \
			actor.getAttribute('int'), actor.getUnmodifiedAttribute('int'), \
			actor.getAttribute('wis'), actor.getUnmodifiedAttribute('wis'), \
			actor.getAttribute('dex'), actor.getUnmodifiedAttribute('dex'), \
			actor.getAttribute('con'), actor.getUnmodifiedAttribute('con'), \
			actor.getAttribute('cha'), actor.getUnmodifiedAttribute('cha'), \
			actor.inventory.getWeight(), actor.getMaxWeight(), \
			actor.trains, actor.practices)
		actor.notify(msg);

class CommandLook(Command):
	name = "look"
	def perform(self, actor, args = []):
		l = len(args)
		if l <= 1:
			# room and exits
			msg = "%s\n%s\n\n[Exits %s]\n" % (actor.room.title, actor.room.description, "".join(direction[:1] for direction, room in actor.room.directions.iteritems() if room))
			# items
			msg += actor.room.inventory.inspection(' is here.')
			# actors
			msg += "\n".join(_actor.long.capitalize() for _actor in actor.room.actors if _actor is not actor)+"\n"
		else:
			lookingAt = matchPartial(args[1:][0], actor.inventory.items, actor.room.inventory.items, actor.room.actors)
			msg = lookingAt.description.capitalize()+"\n" if lookingAt else "Nothing is there."
		actor.notify(msg)

class CommandQuit(Command):
	name = "quit"
	def perform(self, actor, args = []):
		actor.client.disconnect()

class CommandWho(Command):
	name = "who"
	def perform(self, actor, args = []):
		wholist = '';
		for i in actor.client.factory.clients:
			wholist += str(i.user) if i.user else ""
		l = len(actor.client.factory.clients)
		wholist += "\n"+str(l)+" player"+("" if l == 1 else "s")+" found."
		actor.notify(wholist)

class CommandAffects(Command):
	name = "affects"
	def perform(self, actor, args = []):
		actor.notify("Your affects:\n"+"\n".join(str(x)+": "+str(x.timeout)+" ticks" for x in actor.affects));

class MoveDirection(Command):
	requiresStandingDisposition = True
	def perform(self, actor, args = []):
		if actor.target:
			actor.notify("You are fighting!")
			return

		if actor.disposition == Disposition.INCAPACITATED:
			actor.notify("You are incapacitated and will die soon if not aided.")
			return

		newRoom = self.getNewRoom(actor)
		if(newRoom):
			cost = actor.getMovementCost()
			if(actor.attributes.movement >= cost):
				actor.attributes.movement -= cost
				actor.room.notify(actor, str(actor).title()+" leaves "+self.name+".")
				actor.room.actors.remove(actor)
				actor.room = newRoom
				actor.room.actors.append(actor)
				actor.room.notify(actor, str(actor).title()+" has arrived.")
				CommandLook().tryPerform(actor)
			else:
				actor.notify("You are too tired to move.")
		else:
			actor.notify("Alas, nothing is there.")
	
	def getNewRoom(self, actor):
		print "getNewRoom is not defined"
		raise 

class CommandNorth(MoveDirection):
	name = "north"
	def getNewRoom(self, actor):
		return actor.room.directions['north']

class CommandSouth(MoveDirection):
	name = "south"
	def getNewRoom(self, actor):
		return actor.room.directions['south']

class CommandEast(MoveDirection):
	name = "east"
	def getNewRoom(self, actor):
		return actor.room.directions['east']

class CommandWest(MoveDirection):
	name = "west"
	def getNewRoom(self, actor):
		return actor.room.directions['west']

class CommandUp(MoveDirection):
	name = "up"
	def getNewRoom(self, actor):
		return actor.room.directions['up']

class CommandDown(MoveDirection):
	name = "down"
	def getNewRoom(self, actor):
		return actor.room.directions['down']
