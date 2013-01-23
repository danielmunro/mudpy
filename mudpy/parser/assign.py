class Assignable(object):
	def process(self, parser, instance):
		line = parser.readcleanline()
		if not line:
			from parser import ParserException
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
				from mudpy.factory import Factory
				instance.race = Factory.new(Race = value, newWith = instance)
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
		from mudpy.room import Randomhall, Grid, Room, Direction
		from mudpy.item import Door
		from mudpy.utility import startsWith
		if isinstance(instance, Randomhall) and instanceProperty.find('Prob') > -1:
			direction = startsWith(instanceProperty[0:1], Direction.__subclasses__())
			instance.probabilities[direction.name] = value
			return True
		if isinstance(instance, Grid) and instanceProperty.find('Count') > -1:
			direction = startsWith(instanceProperty[0:1], Direction.__subclasses__())
			instance.counts[direction.name] = value
		if issubclass(instance.__class__, Room) or isinstance(instance, Door):
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

class Abilities(Assignable):
	def process(self, parser, instance):
		line = parser.readcleanline()
		if not line:
			from parser import ParserException
			raise ParserException
		from mudpy.factory import Factory
		for i in line.split(","):
			instance.abilities.append(Factory.new(Ability = i.strip()))

class Block(Assignable):
	def __init__(self, propertyName, end = "\n"):
		self.propertyName = propertyName
		if self.propertyName == "description":
			end = "~"
		self.end = end
	
	def process(self, parser, instance):
		setattr(instance, self.propertyName, self._process(parser, ""))
	
	def _process(self, parser, value):
		line = parser.readline()
		if line.find(self.end) > -1:
			return value+line.rstrip(self.end+"\n")
		else:
			return self._process(parser, value+line)
