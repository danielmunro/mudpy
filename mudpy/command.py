from utility import *

class CommandFactory:
	@staticmethod
	def newCommand(name):
		command = startsWith(name, InstanceCommand.__subclasses__());
		return command() if command else None

class InstanceCommand(object):
	name = ""
	def perform(self):
		print "perform() not defined"
		raise
	
	def __str__(self):
		return self.name

class CommandGet(InstanceCommand):
	name = "get"
	def perform(self, actor, args = []):
		item = actor.room.inventory.getItemByName(args[1])
		if item:
			actor.room.inventory.remove(item)
			actor.inventory.append(item)
			actor.notify("You pick up "+str(item)+" off the floor.")
		else:
			actor.notify("Nothing is there.")

class CommandDrop(InstanceCommand):
	name = "drop"
	def perform(self, actor, args = []):
		item = actor.inventory.getItemByName(args[1])
		if item:
			actor.inventory.remove(item)
			actor.room.inventory.append(item)
			actor.notify("You drop "+str(item)+" to the floor.")
		else:
			actor.notify("Nothing is there.")

class CommandInventory(InstanceCommand):
	name = "inventory"
	def perform(self, actor, args = []):
		actor.notify("Your inventory:\n"+actor.inventory.inspection())

class CommandScore(InstanceCommand):
	name = "score"
	def perform(self, actor, args = []):
		msg = "You are %s, a %s\n%i/%i hp %i/%i mana %i/%i mv\nstr (%i/%i), int (%i/%i), wis (%i/%i), dex (%i/%i), con(%i/%i), cha(%i/%i)\n" % ( \
			actor, actor.race, actor.getAttribute('hp'), actor.getMaxAttribute('hp'), actor.getAttribute('mana'), \
			actor.getMaxAttribute('mana'), actor.getAttribute('movement'), actor.getMaxAttribute('movement'), \
			actor.getBaseAttribute('str'), actor.getAttribute('str'), \
			actor.getBaseAttribute('int'), actor.getAttribute('int'), \
			actor.getBaseAttribute('wis'), actor.getAttribute('wis'), \
			actor.getBaseAttribute('dex'), actor.getAttribute('dex'), \
			actor.getBaseAttribute('con'), actor.getAttribute('con'), \
			actor.getBaseAttribute('cha'), actor.getAttribute('cha'))
		actor.notify(msg);

class CommandLook(InstanceCommand):
	name = "look"
	def perform(self, actor, args = []):
		l = len(args)
		if l <= 1:
			# directions
			dirstr = ''
			for i, v in actor.room.directions.iteritems():
				if(v):
					dirstr += i[:1]
			msg = "%s\n%s\n[Exits %s]\n" % (actor.room.title, actor.room.description, dirstr)
			# items
			if len(actor.room.inventory.items):
				msg += actor.room.inventory.inspection()+"\n"
			# actors
			for i, v in enumerate(actor.room.actors):
				if(v is not actor):
					msg += str(v)+" is here.\n"
		else:
			lookat = args[1:][0]
			msg = "Nothing is there."
			lookingAt = matchPartial(lookat, actor.inventory.items, actor.room.inventory.items, actor.room.actors)
			if lookingAt:
				msg = lookingAt.long.capitalize()+".\n"
		actor.notify(msg)

class CommandQuit(InstanceCommand):
	name = "quit"
	def perform(self, actor, args = []):
		actor.client.disconnect()

class CommandWho(InstanceCommand):
	name = "who"
	def perform(self, actor, args = []):
		wholist = '';
		for i in actor.client.factory.clients:
			wholist += str(i.user) if i.user else ""
		l = len(actor.client.factory.clients)
		wholist += "\n"+str(l)+" player"+("" if l == 1 else "s")+" found.\n"
		actor.notify(wholist)

class CommandAffects(InstanceCommand):
	name = "affects"
	def perform(self, actor, args = []):
		actor.notify("Your affects:\n"+"\n".join(str(x)+": "+str(x.timeout)+" ticks" for x in actor.affects)+"\n");

class MoveDirection(InstanceCommand):
	def perform(self, actor, args = []):
		newRoom = self.getNewRoom(actor)
		if(newRoom):
			cost = actor.getMovementCost()
			if(actor.attributes.movement > cost):
				actor.attributes.movement -= cost
				actor.room.notify(actor, str(actor)+" leaves "+self.name+".")
				actor.room.actors.remove(actor)
				actor.room = newRoom
				actor.room.actors.append(actor)
				actor.room.notify(actor, str(actor)+" has arrived.")
				CommandLook().perform(actor)
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
