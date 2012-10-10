import os
from room import *
from actor import Mob
from item import *
from factory import Factory
from utility import *

class Assignable(object):
	def process(self, f, instance):
		line = f.readline().strip()
		if not line:
			raise ParserException
		parts = line.split(",")
		for i in parts:
			kv = i.strip().split(' ', 1)
			if kv[0]:
				try:
					self.assign(instance, kv[0], self.tryParse(kv[1]))
				except AttributeError as e:
					print e
	
	def tryParse(self, value):
		return int(value) if value.isdigit() else value
	
	def assign(self, instance, instanceProperty, value):
		print "assign not implemented"

class Properties(Assignable):
	def assign(self, instance, instanceProperty, value):
		if hasattr(instance, instanceProperty):
			#hack
			if instanceProperty == "race":
				instance.race = Factory.new(Race = value)
			else:
				if value == "true":
					value = True
				elif value == "false":
					value = False
				setattr(instance, instanceProperty, value)
		elif self.aliases(instance, instanceProperty, value):
			pass
		else:
			raise AttributeError('Property "'+instanceProperty+'" is not defined in '+instance.__class__.__name__)
	
	# this function is a hack
	def aliases(self, instance, instanceProperty, value):
		if isinstance(instance, Room) or isinstance(instance, Door):
			direction = startsWith(instanceProperty, Direction.__subclasses__())
			if direction:
				instance.directions[direction.name] = value
			return True
		return False

class Attributes(Assignable):
	def assign(self, instance, instanceProperty, value):
		if hasattr(instance.attributes, instanceProperty):
			setattr(instance.attributes, instanceProperty, value)
			if instanceProperty in ['hp', 'mana', 'movement']:
				setattr(instance.attributes, 'max'+instanceProperty, value)
		else:
			raise AttributeError('Attribute "'+instanceProperty+'" is not defined in '+instance.__class__.__name__)

class Abilities:
	def process(self, f, instance):
		parts = f.readline().split(",")
		for i in parts:
			instance.abilities.append(Factory.new(Ability = i.strip()))

class Block:
	def __init__(self, propertyName, end = "\n"):
		self.propertyName = propertyName
		self.end = end
	
	def process(self, f, instance):
		setattr(instance, self.propertyName, self._process(f, ""))
	
	def _process(self, f, value):
		line = f.readline()
		if line.find(self.end) > -1:
			return value+line.rstrip(self.end+"\n")
		else:
			return self._process(f, value+line)

class Parser:
	definitions = {
		'area': [Properties()],
		'room': [Block('title'), Block('description', '~'), Properties()],
		'mob': [Block('long'), Block('description', '~'), Properties(), Attributes(), Abilities()],
		'container': [Block('name'), Block('description', '~'), Properties()],
		'drink': [Block('name'), Block('description', '~'), Properties()],
		'furniture': [Block('name'), Block('description', '~'), Properties()],
		'item': [Block('name'), Block('description', '~'), Properties()],
		'key': [Block('name'), Block('description', '~'), Properties()],
		'quest': [Block('name')],
		'door': [Block('name'), Block('description', '~'), Properties()],
		'ability': [Block('name'), Properties()]
	}
	def __init__(self, baseDir):
		self.parseDir("scripts/"+baseDir)
		self.initializeRooms()

	def parseDir(self, path):
		listing = os.listdir(path)
		for infile in listing:
			parts = infile.split(".")
			if len(parts) == 1:
				self.parseDir(path+"/"+parts[0])
			elif parts[1] == "area":
				self.parseArea(path+"/"+parts[0]+".area")
	
	def parseArea(self, areaFile):
		f = open(areaFile)
		line = f.readline()
		while line:
			line = self.trim(line)
			if line in self.definitions:
				_class = line.title()
				instance = globals()[_class]()
				try:
					for chunk in self.definitions[line]:
						chunk.process(f, instance)
				except ParserException:
					pass
				if isinstance(instance, Room):
					lastRoom = instance
					lastRoom.area = lastArea
					lastInventory = instance.inventory
					Room.rooms[lastRoom.area.name+":"+str(lastRoom.id)] = lastRoom
				elif isinstance(instance, Mob):
					lastRoom.actors.append(instance)
					lastInventory = instance.inventory
					instance.room = lastRoom
				elif isinstance(instance, Area):
					lastArea = instance
				elif isinstance(instance, Item):
					lastInventory.append(instance)

			line = f.readline()
	
	def trim(self, line):
		line = line.strip()
		commentPos = line.find('#')
		if commentPos > -1:
			line = line[0:commentPos]
		return line
	
	def initializeRooms(self):
		for r, room in Room.rooms.iteritems():
			for d, direction in Room.rooms[r].directions.items():
				if(direction):
					try:
						if type(direction) is int:
							direction = Room.rooms[r].area.name+":"+str(direction)
						Room.rooms[r].directions[d] = Room.rooms[direction]
					except KeyError:
						print "Room id "+str(direction)+" is not defined, removing"
						del Room.rooms[r].directions[d]

class ParserException(Exception):
	pass
