import debug, heartbeat
from room import Room, Randomhall, Grid, Area
from item import Item, Drink
from actor import Mob, Ability
#import actor

import os, json, operator

wireframes = {}
depends = []
loaded = []
deferred = []
lastarea = None
INITFILE = 'init.json'

def new(instance, name):
	global wireframes

	try:
		found = wireframes[instance.__class__.__name__][name]
	except KeyError:
		raise FactoryException("Factory does not know how to create "+name)
	return buildFromDefinition(instance, found[instance.__class__.__name__])

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
					match['priority'] = wireframe[key]['priority']
				except KeyError:
					match['priority'] = 0
				matches.append(match)
	matches = sorted(matches, key=operator.itemgetter('priority'))
	matches.reverse()
	try:
		return matches[0] if scalar else matches
	except IndexError:
		return None

def parse(path):
	global deferred, loaded

	_parse(path)
	while len(deferred):
		startlen = len(loaded)
		_deferred = deferred
		deferred = []
		for fullpath in _deferred:
			_parse(fullpath)
		endlen = len(loaded)
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
					debug.log("Room id "+str(direction)+" is not defined, removing", "notice")
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

def _parse(path):
	global INITFILE

	debug.log('recurse through path: '+path)

	if path.endswith('.json'):
		return parseJson(path) # parse the json file

	# check that dependencies for the directory have been met
	init = path+'/'+INITFILE
	if os.path.isfile(init) and not parseJson(init):
		return

	if os.path.isdir(path):
		# parse through this directory
		for infile in os.listdir(path):
			fullpath = path+'/'+infile
			if fullpath == init:
				continue # skip the init file
			_parse(fullpath)

def parseJson(scriptFile):
	global loaded, deferred

	debug.log('parsing json file: '+scriptFile)
	fp = open(scriptFile)
	try:
		data = json.load(fp)
	except ValueError:
		debug.log("script file is not properly formatted: "+scriptFile, "error")
	path, filename = os.path.split(scriptFile)
	try:
		_parseJson(data)
		loaded.append(filename)
		return True
	except DependencyException:
		debug.log(scriptFile+' deferred')
		deferred.append(path if filename == INITFILE else scriptFile)
		return False

def _parseJson(data, parent = None):
	instances = []
	for item in data:
		for _class in item:
			_class = str(_class)
			try:
				instance = globals()[_class]()
			except KeyError as e:
				instance = None
			instances.append(buildFromDefinition(instance, item[_class], parent))
	return instances

def buildFromDefinition(instance, properties, parent = None):
	for descriptor in properties:
		fn = 'descriptor'+descriptor.title()
		value = properties[descriptor]
		if isinstance(value, unicode):
			value = str(value)
		try:
			globals()[fn](instance, properties[descriptor])
		except KeyError: pass
	fn = 'doneParse'+instance.__class__.__name__
	try:
		globals()[fn](parent, instance)
	except KeyError: pass
	return instance

def descriptorWireframes(none, wireframes):
	add(wireframes)

def descriptorAbilities(instance, abilities):
	for ability in abilities:
		instance.abilities.append(new(Ability(), ability))

def descriptorAffects(instance, affects):
	import affect
	for aff in affects:
		instance.affects.append(new(affect.Affect(), aff))

def descriptorProficiencies(actor, proficiencies):
	for proficiency in proficiencies:
		actor.addProficiency(proficiency, proficiencies[proficiency])

def descriptorInventory(instance, inventory):
	_parseJson(inventory, instance)

def descriptorMobs(instance, mobs):
	_parseJson(mobs, instance)

def descriptorProperties(instance, properties):
	for prop in properties:
		setattr(instance, prop, properties[prop])

def descriptorAttributes(instance, attributes):
	for attribute in attributes:
		setattr(instance.attributes, attribute, attributes[attribute])

def doneParseDepends(parent, depends):
	global loaded

	deps = [dep for dep in depends.on if not dep in loaded]
	if len(deps):
		raise DependencyException

def doneParseArea(parent, area):
	global lastarea

	lastarea = area

def doneParseMob(parent, mob):
	import actor
	parent.actors.append(mob)
	mob.room = parent
	mob.race = new(actor.Race(), mob.race)
	heartbeat.instance.attach('tick', mob.tick)

def doneParseRoom(parent, room):
	global lastarea

	room.area = lastarea
	Room.rooms[room.area.name+":"+str(room.id)] = room

def doneParseItem(parent, item):
	parent.inventory.append(item)

def doneParseDrink(parent, drink):
	parent.inventory.append(drink)
	
class Depends:
	def __init__(self):
		self.on = []

class DependencyException(Exception): pass
class ParserException(Exception): pass
class FactoryException(Exception): pass
