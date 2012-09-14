from item import Inventory

class Room:
	rooms = {}

	def __init__(self):
		self.id = 0
		self.title = ''
		self.description = ''
		self.actors = []
		self.inventory = Inventory()
		self.directions = dict((getattr(direction, 'name'), None) for direction in Direction.__subclasses__())
	
	def notify(self, actor, message):
		for i, k in enumerate(self.actors):
			if k is actor:
				continue
			else:
				k.notify(message)
	
	def getActorByName(self, name):
		for i in iter(self.actors):
			if i.name.lower().find(name.lower()) > -1:
				return i
	
	def __str__(self):
		return self.id

class Direction(object):
	name = ""

	def __str__(self):
		return self.name

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
