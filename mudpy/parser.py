import os
from room import Area, Room
from actor import Mob
from item import Item, Container, Drink, Door

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
					self.assign(instance, kv[0], kv[1])
				except AttributeError as e:
					print e
	
	def assign(self, instance, instanceProperty, value):
		print "assign not implemented"

class Properties(Assignable):
	def assign(self, instance, instanceProperty, value):
		if hasattr(instance, instanceProperty):
			setattr(instance, instanceProperty, value)
		elif self.aliases(instance, instanceProperty, value):
			pass
		else:
			raise AttributeError('Property "'+instanceProperty+'" is not defined in '+instance.__class__.__name__)
	
	# this function is a hack
	def aliases(self, instance, instanceProperty, value):
		if isinstance(instance, Room):
			if instanceProperty == "n":
				instance.directions["north"] = value
			elif instanceProperty == "s":
				instance.directions["south"] = value
			elif instanceProperty == "e":
				instance.directions["east"] = value
			elif instanceProperty == "w":
				instance.directions["west"] = value
			elif instanceProperty == "u":
				instance.directions["up"] = value
			elif instanceProperty == "d":
				instance.directions["down"] = value
			return True
		return False

class Attributes(Assignable):
	def assign(self, instance, instanceProperty, value):
		if hasattr(instance.attributes, instanceProperty):
			setattr(instance.attributes, instanceProperty, value)
			setattr(instance.max_attributes, instanceProperty, value)
		else:
			raise AttributeError('Attribute "'+instanceProperty+'" is not defined in '+instance.__class__.__name__)

class Line:
	def __init__(self, propertyName):
		self.propertyName = propertyName
	
	def process(self, f, instance):
		setattr(instance, self.propertyName, f.readline().strip())

class Block:
	def __init__(self, propertyName):
		self.propertyName = propertyName
	
	def process(self, f, instance):
		setattr(instance, self.propertyName, self._process(f, ""))
	
	def _process(self, f, value):
		line = f.readline().strip()
		if line.find("~") > -1:
			return value+line.strip("~")
		else:
			return self._process(f, value+line+"\n")


class Abilities:
	def process(self, f, instance):
		line = f.readline().strip()
		if not line:
			raise ParserException
		parts = line.split(",")

class Parser:
	definitions = {
		'area': [Properties()],
		'room': [Line('title'), Block('description'), Properties()],
		'mob': [Line('long'), Block('description'), Properties(), Attributes(), Abilities()],
		'container': [Line('long'), Block('description'), Properties()],
		'drink': [Line('long'), Block('description'), Properties()],
		'item': [Line('long'), Block('description'), Properties()],
		'quest': [Block('name')],
		'door': [Line('long'), Block('description'), Properties()]
	}
	def __init__(self, baseDir):
		self.parseDir(baseDir)
		for r, room in Room.rooms.iteritems():
			for d, direction in Room.rooms[r].directions.iteritems():
				if(direction):
					try:
						Room.rooms[r].directions[d] = Room.rooms[Room.rooms[r].area.name+":"+direction]
					except KeyError:
						print "Room id "+str(direction)+" is not defined"


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
					Room.rooms[lastRoom.area.name+":"+lastRoom.id] = lastRoom
				elif isinstance(instance, Mob):
					lastRoom.appendActor(instance)
				elif isinstance(instance, Area):
					lastArea = instance
			line = f.readline()
	
	def trim(self, line):
		line = line.strip()
		commentPos = line.find('#')
		if commentPos > -1:
			line = line[0:commentPos]
		return line

class ParserException(Exception):
	pass
