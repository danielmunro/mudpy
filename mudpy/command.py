class Command:
	commands = [
		'north',
		'south',
		'east',
		'west',
		'up',
		'down',
		'who',
		'quit',
		'look',
		'score',
		'inventory',
		'get',
		'drop'
	]

	def __init__(self, actor, args):
		args = args.split()
		if len(args):
			i = self.getCommandIndexFromArg(args[0])
			if i > -1:
				instance = globals()[self.getCommandClassFromIndex(i)]()
				instance.perform(actor, args)
			else:
				actor.notify("What was that?")
	
	def getCommandIndexFromArg(self, arg):
		for i, k in enumerate(self.commands):
			if(k.find(arg) == 0):
				return i
		return -1
	
	def getCommandClassFromIndex(self, i):
		return 'Command'+self.commands[i].title();

class InstanceCommand(object):
	def perform(self):
		print "perform() not defined"
		raise

class CommandGet(InstanceCommand):
	def perform(self, actor, args = []):
		item = actor.room.inventory.getByName(args[1])
		if item:
			actor.room.inventory.remove(item)
			actor.inventory.append(item)
			actor.notify("You pick up "+str(item)+" off the floor.")
		else:
			actor.notify("Nothing is there.")

class CommandDrop(InstanceCommand):
	def perform(self, actor, args = []):
		item = actor.inventory.getByName(args[1])
		if item:
			actor.inventory.remove(item)
			actor.room.inventory.append(item)
			actor.notify("You drop "+str(item)+" to the floor.")
		else:
			actor.notify("Nothing is there.")

class CommandInventory(InstanceCommand):
	def perform(self, actor, args = []):
		actor.notify("Your inventory:\n"+actor.inventory.inspection())

class CommandScore(InstanceCommand):
	def perform(self, actor, args = []):
		a = actor.attributes
		m = actor.max_attributes
		actor.notify("You are %s.\n%i/%i hp %i/%i mana %i/%i mv\n" % (actor.name, a.hp, m.hp, a.mana, m.mana, a.movement, m.movement));

class CommandLook(InstanceCommand):
	def perform(self, actor, args = []):
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
		actor.notify(msg)

class CommandQuit(InstanceCommand):
	def perform(self, actor, args = []):
		actor.client.disconnect()

class CommandWho(InstanceCommand):
	def perform(self, actor, args = []):
		wholist = '';
		for i in actor.client.factory.clients:
			wholist += str(i.user) if i.user else ""
		l = len(actor.client.factory.clients)
		wholist += "\n"+str(l)+" player"+("" if l == 1 else "s")+" found.\n"
		actor.notify(wholist)

class MoveDirection(InstanceCommand):
	def perform(self, actor, args = []):
		newRoom = self.getNewRoom(actor)
		if(newRoom):
			cost = actor.getMovementCost()
			if(actor.attributes.movement > cost):
				actor.attributes.movement -= cost
				actor.room.notify(actor, str(actor)+" leaves "+self.command+".")
				actor.room.removeActor(actor)
				actor.room = newRoom
				actor.room.appendActor(actor)
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
	command = "north"
	def getNewRoom(self, actor):
		return actor.room.directions['north']

class CommandSouth(MoveDirection):
	command = "south"
	def getNewRoom(self, actor):
		return actor.room.directions['south']

class CommandEast(MoveDirection):
	command = "east"
	def getNewRoom(self, actor):
		return actor.room.directions['east']

class CommandWest(MoveDirection):
	command = "west"
	def getNewRoom(self, actor):
		return actor.room.directions['west']

class CommandUp(MoveDirection):
	command = "up"
	def getNewRoom(self, actor):
		return actor.room.directions['up']

class CommandDown(MoveDirection):
	command = "down"
	def getNewRoom(self, actor):
		return actor.room.directions['down']
