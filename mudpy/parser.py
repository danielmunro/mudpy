from mudpy.debug import Debug
from mudpy.ability import Ability
from mudpy.affect import Affect
from mudpy.proficiency import Proficiency
from mudpy.race import Race
from mudpy.room import Room, Randomhall, Grid, Area
from mudpy.actor import Mob
from mudpy.item import Item, Drink
from mudpy.depends import Depends

import os, json

class Parser:
	BASEPATH = 'mudpy'
	_globals = []

	def __init__(self):
		self.loaded = []
		self.deferred = []
		self.depends = []
		self.lastroom = None

	def parseDir(self, path):
		Debug.log('parsing scripts for '+path)
		for infile in os.listdir(path):
			fullpath = path+'/'+infile
			if os.path.isdir(fullpath):
				# recurse through scripts directory tree
				self.parseDir(fullpath)
			elif fullpath.endswith('.json'):
				try:
					self.parseJson(fullpath)
					self.loaded.append(infile)
				except DependencyException:
					self.deferred.append(fullpath)
	
	def parseJson(self, scriptFile):
		Debug.log('parsing json script file: '+scriptFile)
		fp = open(scriptFile)
		data = json.load(fp)
		self._parseJson(None, data)
	
	def _parseJson(self, parent, data):
		from mudpy.factory import Factory
		for item in data:
			for _class in item:
				_class = str(_class)
				instance = globals()[_class]()
				for descriptor in item[_class]:
					if descriptor == 'properties':
						for prop in item[_class][descriptor]:
							setattr(instance, prop, self.guessType(item[_class][descriptor][prop]))
					elif descriptor == 'affects':
						for affect in item[_class][descriptor]:
							instance.affects.append(Factory.new(Affect=affect))
					elif descriptor == "attributes":
						for attribute in item[_class][descriptor]:
							setattr(instance.attributes, attribute, self.guessType(item[_class][descriptor][attribute]))
					elif descriptor == "proficiencies":
						for prof, level in item[_class][descriptor].iteritems():
							instance.addProficiency(prof, level)
					elif descriptor == "mobs" or descriptor == "inventory":
						self._parseJson(instance, item[_class][descriptor])
				getattr(self, 'doneParse'+_class)(parent, instance)
	
	def doneParseAffect(self, parent, affect):
		Parser._globals.append(affect)

	def doneParseRace(self, parent, race):
		Parser._globals.append(race)
	
	def doneParseAbility(self, parent, ability):
		from mudpy.ability import Ability
		Ability.instances.append(ability)
	
	def doneParseProficiency(self, parent, proficiency):
		Parser._globals.append(proficiency)
	
	def doneParseDepends(self, parent, depends):
		deps = [dep for dep in depends.on if not dep in self.loaded]
		if len(deps):
			raise DependencyException
	
	def doneParseArea(self, parent, area):
		self.lastarea = area

	def doneParseMob(self, parent, mob):
		parent.actors.append(mob)
		mob.room = parent

	def doneParseRoom(self, parent, room):
		room.area = self.lastarea
		Room.rooms[room.area.name+":"+str(room.id)] = room

	def doneParseItem(self, parent, item):
		parent.inventory.append(item)

	def doneParseDrink(self, parent, drink):
		parent.inventory.append(drink)

	@staticmethod
	def parse(path):
		p = Parser()
		p.parseDir(Parser.BASEPATH+'/'+path)
		for fullpath in p.deferred:
			p.parseJson(fullpath)

		#build out the room tree
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

	@staticmethod
	def guessType(value):
		try:
			if value.isdigit():
				return int(value)
			try:
				return float(value)
			except ValueError: pass
		except AttributeError: pass
		if value == "True":
			return True
		if value == "False":
			return False
		return value
	
class ParserException(Exception): pass
class DependencyException(Exception): pass
