from item import Inventory
from random import random, choice

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
	
	def notify(self, notifier, message):
		for actor in list(actor for actor in self.actors if not actor is notifier):
			actor.notify(message+"\n")
	
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
			for actor in list(set(self.actors) - set(announcedActors)):
				actor.notify(generalMessage+"\n")
	
	def mobs(self):
		from actor import Mob
		return list(actor for actor in self.actors if isinstance(actor, Mob))

class Randomhall(Room):
	def __init__(self):
		super(Randomhall, self).__init__()
		self.rooms = 0
		self.exit = 0
		self.probabilities = dict((direction, .5) for direction in self.directions)
	
	def buildDungeon(self, roomCount = 0):
		direction = Direction.getRandom(list(direction for direction, room in self.directions.iteritems() if not room))
		if self.probabilities[direction] > random():
			if self.rooms < roomCount:
				exit = Room.rooms[self.area.name+":"+str(self.exit)]
				self.directions[direction] = exit
				exit.directions[Direction.getReverse(direction)] = self
			else:
				return self.createTo(direction).buildDungeon(roomCount+1)
		else:
			rooms = list(room for room in self.directions.values() if isinstance(room, Randomhall))
			if rooms:
				return choice(rooms).buildDungeon(roomCount)
		return roomCount;
	
	def createTo(self, direction):
		r = Randomhall()
		r.title = self.title
		r.description = self.description
		r.rooms = self.rooms
		r.exit = self.exit
		r.probabilities = self.probabilities
		r.area = self.area
		self.directions[direction] = r
		r.directions[Direction.getReverse(direction)] = self
		return r


class Direction(object):
	name = ""
	
	@staticmethod
	def getRandom(allowedDirections = []):
		return choice(allowedDirections if allowedDirections else list(direction.name for direction in Direction.__subclasses__()))
	
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
