from parser import Parser

class AreaParser(Parser):
	def __init__(self):
		self.lastroom = None
		self.lastinventory = None
		self.lastarea = None
		super(AreaParser, self).__init__('areas', self.parseArea, self.parseJsonArea)

	def parseJsonArea(self, parent, instance):
		from mudpy.room import Room, Randomhall, Grid, Area
		from mudpy.actor import Mob
		from mudpy.item import Item, Door, Key, Furniture, Container, Food, Drink, Weapon, Armor, Equipment
		if issubclass(instance.__class__, Room):
			instance.area = self.lastarea
			self.lastroom = instance
			self.lastinventory = instance.inventory
			Room.rooms[self.lastroom.area.name+":"+str(self.lastroom.id)] = self.lastroom
		elif isinstance(instance, Mob):
			parent.actors.append(instance)
			self.lastinventory = instance.inventory
			instance.room = parent
		elif isinstance(instance, Item):
			parent.inventory.append(instance)
		elif isinstance(instance, Area):
			self.lastarea = instance
	
	def parseArea(self, _class):
		from mudpy.room import Room, Randomhall, Grid, Area
		from mudpy.actor import Mob
		from mudpy.item import Item, Door, Key, Furniture, Container, Food, Drink, Weapon, Armor, Equipment
		instance = self.applyDefinitionsTo(locals()[_class]())
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

	def finishInitialization(self):
		randomHalls = []
		grids = []
		from mudpy.room import Room, Randomhall, Grid
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
