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
		'look'
	]

	def __init__(self, actor, args):
		args = args.split()
		i = self.getCommandIndexFromArg(args[0])
		if i > -1:
			globals()[self.getCommandClassFromIndex(i)](actor, self.commands[i], args)
		else:
			actor.notify("What was that?")
	
	def getCommandIndexFromArg(self, arg):
		for i, k in enumerate(self.commands):
			if(k.find(arg) == 0):
				return i
		return -1
	
	def getCommandClassFromIndex(self, i):
		return 'Command'+self.commands[i].title();

class ArgumentException(Exception):
	def __init__(self, value):
		self.value = value

class InstanceCommand(object):
	def __init__(self, actor, command, args):
		try:
			self.perform(actor, command, self.parseArgs(args))
		except ArgumentException as e:
			actor.notify(e.value)
	
	def perform(self):
		print "perform() not defined"
		raise
	
	def parseArgs(self, args):
		return args


class CommandLook(InstanceCommand):
	def perform(self, actor, command, args):
		actor.look()

class CommandQuit(InstanceCommand):
	def perform(self, actor, command, args):
		actor.client.disconnect()

class CommandWho(InstanceCommand):
	def perform(self, actor, command, args):
		wholist = '';
		for i in actor.client.factory.clients:
			wholist += str(i.user) if i.user else ""
		l = len(actor.client.factory.clients)
		wholist += "\n"+str(l)+" player"+("" if l == 1 else "s")+" found.\n"
		actor.notify(wholist)

class MoveDirection(InstanceCommand):
	def perform(self, actor, command, args):
		newRoom = self.getNewRoom(actor)
		if(newRoom):
			actor.room.notify(actor, str(actor)+" leaves "+command+".")
			actor.room.removeActor(actor)
			actor.room = newRoom
			actor.room.addActor(actor)
			actor.room.notify(actor, str(actor)+" has arrived.")
			actor.look()
		else:
			actor.notify("Alas, nothing is there.")
	
	def getNewRoom(self, actor):
		print "getNewRoom is not defined"
		raise 

class CommandNorth(MoveDirection):
	def getNewRoom(self, actor):
		return actor.room.directions['north']

class CommandSouth(MoveDirection):
	def getNewRoom(self, actor):
		return actor.room.directions['south']

class CommandEast(MoveDirection):
	def getNewRoom(self, actor):
		return actor.room.directions['east']

class CommandWest(MoveDirection):
	def getNewRoom(self, actor):
		return actor.room.directions['west']

class CommandUp(MoveDirection):
	def getNewRoom(self, actor):
		return actor.room.directions['up']

class CommandDown(MoveDirection):
	def getNewRoom(self, actor):
		return actor.room.directions['down']
