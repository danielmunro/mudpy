import debug, heartbeat
from affect import Affect
from proficiency import Proficiency
from room import Room, Randomhall, Grid, Area
from actor import Mob, Race, Ability
from item import Item, Drink

import os, json, operator

wireframes = {}

def new(instance, name):
	global wireframes

	try:
		found = wireframes[instance.__class__.__name__][name]
	except KeyError:
		raise FactoryException("Factory does not know how to create "+name)
	p = Parser()
	return p.buildFromDefinition(instance, found[instance.__class__.__name__])

def add(newwireframes):
	global wireframes

	for wireframe in newwireframes:
		for key, blob in wireframe.iteritems():
			name = blob['properties']['name']
			try:
				wireframes[key][name] = wireframe
			except KeyError:
				wireframes[key] = {}
				wireframes[key][name] = wireframe

def match(name, keys, scalar = True):
	global wireframes

	matches = []
	if not isinstance(keys, list):
		keys = [keys]
	for key in keys:
		for wireframename, wireframe in wireframes[key].iteritems():
			if wireframename.startswith(name):
				match = {'key':key, 'wireframe':wireframename}
				try:
					match['priority'] = wireframe['priority']
				except KeyError:
					match['priority'] = 0
				matches.append(match)
	matches = sorted(matches, key=operator.itemgetter('priority'))
	try:
		return matches[0] if scalar else matches
	except IndexError:
		return None

def parse(path):
	p = Parser()
	p.parse(path)
	while len(p.deferred):
		startlen = len(p.loaded)
		deferred = p.deferred
		p.deferred = []
		for fullpath in deferred:
			p.parse(fullpath)
		endlen = len(p.loaded)
		if startlen == endlen:
			debug.log("dependencies cannot be met", "error")

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

class Parser:
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
		debug.log('recurse through path: '+path)

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
		debug.log('parsing json file: '+scriptFile)
		fp = open(scriptFile)
		try:
			data = json.load(fp)
		except ValueError:
			debug.log("script file is not properly formatted: "+scriptFile, "error")
		path, filename = os.path.split(scriptFile)
		try:
			self._parseJson(data)
			self.loaded.append(filename)
			return True
		except DependencyException:
			debug.log(scriptFile+' deferred')
			self.deferred.append(path if filename == self.INITFILE else scriptFile)
			return False

	def _parseJson(self, data, parent = None):
		instances = []
		for item in data:
			for _class in item:
				_class = str(_class)
				try:
					instance = globals()[_class]()
				except KeyError:
					instance = None
				instances.append(self.buildFromDefinition(instance, item[_class], parent))
		return instances

	def buildFromDefinition(self, instance, properties, parent = None):
		for descriptor in properties:
			fn = 'descriptor'+descriptor.title()
			value = properties[descriptor]
			if isinstance(value, unicode):
				value = str(value)
			try:
				getattr(self, fn)(instance, properties[descriptor])
			except AttributeError: pass
		fn = 'doneParse'+instance.__class__.__name__
		try:
			getattr(self, fn)(parent, instance)
		except AttributeError: pass
		return instance
	
	def descriptorWireframes(self, none, wireframes):
		add(wireframes)
	
	def descriptorAbilities(self, instance, abilities):
		for ability in abilities:
			instance.abilities.append(new(Ability(), ability))

	def descriptorAffects(self, instance, affects):
		for affect in affects:
			instance.affects.append(new(Affect(), affect))

	def descriptorProficiencies(self, actor, proficiencies):
		for proficiency in proficiencies:
			actor.addProficiency(proficiency, proficiencies[proficiency])

	def descriptorInventory(self, instance, inventory):
		self._parseJson(inventory, instance)
	
	def descriptorMobs(self, instance, mobs):
		self._parseJson(mobs, instance)
	
	def descriptorProperties(self, instance, properties):
		for prop in properties:
			setattr(instance, prop, properties[prop])
	
	def descriptorAttributes(self, instance, attributes):
		for attribute in attributes:
			setattr(instance.attributes, attribute, attributes[attribute])
	
	def doneParseDepends(self, parent, depends):
		deps = [dep for dep in depends.on if not dep in self.loaded]
		if len(deps):
			raise DependencyException
	
	def doneParseArea(self, parent, area):
		self.lastarea = area

	def doneParseMob(self, parent, mob):
		parent.actors.append(mob)
		mob.room = parent
		mob.race = new(Race(), mob.race)
		heartbeat.instance.attach('tick', mob.tick)

	def doneParseRoom(self, parent, room):
		room.area = self.lastarea
		Room.rooms[room.area.name+":"+str(room.id)] = room

	def doneParseItem(self, parent, item):
		parent.inventory.append(item)

	def doneParseDrink(self, parent, drink):
		parent.inventory.append(drink)
	
class Depends:
	def __init__(self):
		self.on = []

class DependencyException(Exception): pass
class ParserException(Exception): pass
class FactoryException(Exception): pass
