from parser import Parser, ParserException
from room import Room, Randomhall, Grid, Area
from actor import Mob
from item import *
from assign import Properties, Block, Attributes, Abilities

class AreaParser(Parser):
	def __init__(self):
		self.lastroom = None
		self.lastinventory = None
		self.lastarea = None
		super(AreaParser, self).__init__('areas', 'parseArea')
	
	def parseArea(self, line):
		if line in self.definitions:
			_class = line.title()
			instance = globals()[_class]()
			try:
				for chunk in self.definitions[line]:
					chunk.process(self, instance)
			except ParserException:
				pass
			if issubclass(instance.__class__, Room):
				self.lastroom = instance
				self.lastroom.area = self.lastarea
				self.lastinventory = instance.inventory
				Room.rooms[self.lastroom.area.name+":"+str(self.lastroom.id)] = self.lastroom
			elif isinstance(instance, Mob):
				self.lastroom.actors.append(instance)
				self.lastinventory = instance.inventory
				instance.room = self.lastroom
			elif isinstance(instance, Area):
				self.lastarea = instance
			elif isinstance(instance, Item):
				self.lastinventory.append(instance)
		elif line:
			print '[error] "'+line+'" is not a parser definition'

	def initializeRooms(self):
		randomHalls = []
		grids = []
		for r, room in Room.rooms.iteritems():
			if isinstance(room, Randomhall):
				randomHalls.append(room)
			if isinstance(room, Grid):
				grids.append(room)
			for d, direction in Room.rooms[r].directions.items():
				if direction:
					try:
						if type(direction) is int:
							direction = Room.rooms[r].area.name+":"+str(direction)
						Room.rooms[r].directions[d] = Room.rooms[direction]
					except KeyError:
						print "Room id "+str(direction)+" is not defined, removing"
						del Room.rooms[r].directions[d]
		for room in randomHalls:
			roomCount = room.buildDungeon()
			while roomCount < room.rooms:
				roomCount = room.buildDungeon(roomCount)
		for room in grids:
			rows = room.counts['west'] + room.counts['east']
			rows = rows if rows > 0 else 1
			cols = room.counts['north'] + room.counts['south']
			cols = cols if cols > 0 else 1
			grid = [[0 for row in range(rows)] for col in range(cols)]
			grid[room.counts['north']-1][room.counts['west']-1] = room
			room.buildDungeon(0, 0, grid)
