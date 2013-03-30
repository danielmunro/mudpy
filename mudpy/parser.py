from mudpy.debug import Debug
from mudpy.ability import Ability
from mudpy.affect import Affect
from mudpy.proficiency import Proficiency
from mudpy.race import Race
from mudpy.room import Room, Randomhall, Grid, Area
from mudpy.actor import Mob
from mudpy.item import Item, Drink
from mudpy.depends import Depends, DependencyException
from factory import Factory

import os, json

class Parser:
	BASEPATH = 'mudpy'
	INITFILE = 'init.json'
	_globals = []

	def __init__(self):
		self.loaded = []
		self.deferred = []
		self.depends = []
		self.lastroom = None

	def parse(self, path):
		if os.path.isdir(path):
			self.parseDir(path) # recurse through scripts directory tree
		elif path.endswith('.json'):
			self.parseJson(path) # parse the json file

	def parseDir(self, path):
		Debug.log('recurse through path: '+path)

		# check that dependencies for the directory have been met
		init = path+'/'+self.INITFILE
		if os.path.isfile(init) and not self.parseJson(init):
			return

		# parse through this directory
		for infile in os.listdir(path):
			fullpath = path+'/'+infile
			if fullpath == init:
				continue # skip the init file
			self.parse(fullpath)

	def parseJson(self, scriptFile):
		Debug.log('parsing json file: '+scriptFile)
		fp = open(scriptFile)
		data = json.load(fp)
		path, filename = os.path.split(scriptFile)
		try:
			self._parseJson(None, data)
			self.loaded.append(filename)
			return True
		except DependencyException:
			Debug.log(scriptFile+' deferred')
			self.deferred.append(path if filename == self.INITFILE else scriptFile)
			return False

	def _parseJson(self, parent, data):
		for item in data:
			for _class in item:
				_class = str(_class)
				instance = globals()[_class]()
				try:
					for descriptor in item[_class]:
						fn = 'descriptor'+descriptor.title()
						value = item[_class][descriptor]
						if isinstance(value, unicode):
							value = str(value)
						getattr(self, fn)(instance, item[_class][descriptor])
					fn = 'doneParse'+_class
					getattr(self, fn)(parent, instance)
				except AttributeError:
					Debug.log("expected function does not exist: Parser."+fn, "error")

	def descriptorSkills(self, instance, skills):
		#self._parseJson(instance, skills)
		pass

	def descriptorAffects(self, instance, affects):
		for affect in affects:
			instance.affects.append(Factory.new(Affect=affect))

	def descriptorProficiencies(self, actor, proficiencies):
		for proficiency in proficiencies:
			actor.addProficiency(proficiency, proficiencies[proficiency])

	def descriptorInventory(self, instance, inventory):
		self._parseJson(instance, inventory)
	
	def descriptorMobs(self, instance, mobs):
		self._parseJson(instance, mobs)
	
	def descriptorProperties(self, instance, properties):
		for prop in properties:
			setattr(instance, prop, properties[prop])
	
	def descriptorAttributes(self, instance, attributes):
		for attribute in attributes:
			setattr(instance.attributes, attribute, attributes[attribute])
	
	def doneParseAffect(self, parent, affect):
		Parser._globals.append(affect)

	def doneParseRace(self, parent, race):
		Parser._globals.append(race)
	
	def doneParseAbility(self, parent, ability):
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
		mob.race = Factory.new(Race=mob.race)

	def doneParseRoom(self, parent, room):
		room.area = self.lastarea
		Room.rooms[room.area.name+":"+str(room.id)] = room

	def doneParseItem(self, parent, item):
		parent.inventory.append(item)

	def doneParseDrink(self, parent, drink):
		parent.inventory.append(drink)

	@staticmethod
	def startParse(path):
		p = Parser()
		p.parse(Parser.BASEPATH+'/'+path)
		while len(p.deferred):
			startlen = len(p.loaded)
			deferred = p.deferred
			p.deferred = []
			for fullpath in deferred:
				p.parse(fullpath)
			endlen = len(p.loaded)
			if startlen == endlen:
				Debug.log("dependencies cannot be met", "error")

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
	
class ParserException(Exception): pass
