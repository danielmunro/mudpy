from item import Inventory

class Room(object):
	rooms = {}

	def __init__(self):
		self.id = 0
		self.title = ''
		self.description = ''
		self.actors = []
		self.inventory = Inventory()
		self.directions = dict((getattr(direction, 'name'), None) for direction in Direction.__subclasses__())
		self.area = None
	
	def notify(self, actor, message):
		for i, k in enumerate(self.actors):
			if k is actor:
				continue
			else:
				k.notify(message+"\n")
	
	def announce(self, messages):
		announcedActors = []
		generalMessage = ""
		for actor, message in messages.iteritems():
			if actor == "*":
				generalMessage = message
			else:
				actor.notify(message+"\n")
				announcedActors.append(actor)
		if generalMessage:
			needAnnouncements = list(set(self.actors) - set(announcedActors))
			for actor in needAnnouncements:
				actor.notify(generalMessage+"\n")
	
	def getActorByName(self, name):
		for i in iter(self.actors):
			if i.name.lower().find(name.lower()) > -1:
				return i

class Randomhall(Room):
	def __init__(self):
		super(Randomhall, self).__init__()
		self.rooms = 0
		self.exit = 0
		self.probabilities = dict((direction.name, .5) for direction in Direction.__subclasses__())
	
	def buildDungeon(self, roomCount = 0):
		possibleDirections = list(direction for direction, room in self.directions.iteritems() if not room)
		direction = None
		import random
		from random import choice
		d = Direction.getRandom(possibleDirections)
		r = random.random()
		if self.probabilities[d] > r:
			direction = d
		else:
			rooms = list(room for room in self.directions.values() if isinstance(room, Randomhall))
			if rooms:
				return choice(rooms).buildDungeon(roomCount)
			return roomCount;

		if self.rooms < roomCount:
			exit = Room.rooms[self.area.name+":"+str(self.exit)]
			self.directions[direction] = exit
			exit.directions[Direction.getReverse(direction)] = self
		else:
			r = Randomhall()
			r.title = self.title
			r.description = self.description
			r.rooms = self.rooms
			r.exit = self.exit
			r.probabilities = self.probabilities
			r.area = self.area
			self.directions[direction] = r
			r.directions[Direction.getReverse(direction)] = self
			return r.buildDungeon(roomCount+1)
		return roomCount

class Direction(object):
	name = ""

	def __str__(self):
		return self.name
	
	@staticmethod
	def getRandom(allowedDirections = []):
		from random import choice
		if not allowedDirections:
			allowedDirections = list(direction.name for direction in Direction.__subclasses__())
		return choice(allowedDirections)
	
	@staticmethod
	def getReverse(direction):
		if direction == "north":
			return "south"
		elif direction == "south":
			return "north"
		elif direction == "east":
			return "west"
		elif direction == "west":
			return "east"
		elif direction == "up":
			return "down"
		elif direction == "down":
			return "up"

class North(Direction):
	name = "north"

class South(Direction):
	name = "south"

class East(Direction):
	name = "east"

class West(Direction):
	name = "west"

class Up(Direction):
	name = "up"

class Down(Direction):
	name = "down"

class Area:
	def __init__(self):
		self.name = ""
		self.terrain = ""
		self.location = ""
