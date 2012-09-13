from attributes import Attributes
from heartbeat import Heartbeat
from actor import User

class Affect(object):
	def __init__(self, affected):
		self.name = "an affect"
		self.wearOffMessage = ""
		self.attributes = Attributes()
		self.timeout = 0
		self.affected = affected
	
	def start(self):
		Heartbeat.instance.attach(self)
		self.affected.affects.append(self)
	
	def tick(self):
		self.timeout -= 1
		if self.timeout < 0:
			Heartbeat.instance.detach(self)
			self.affected.affects.remove(self)
			if isinstance(self.affected, User) and self.wearOffMessage:
				self.affected.notify(self.wearOffMessage)


"""
class AttributeModifier:
	def __init__(self):
		self.attribute_modified = ""
		self.amount = 0
		self.timeout = -1
		self.receiver = None
	
	def apply(self, invoker, receiver):
		global heartbeat
		self.receiver = receiver

		if not self.amount:
			self.amount = self.calculateEffectiveness(invoker, self.receiver)
		setattr(self.receiver.attributes, self.attribute_modified, self.amount)
		setattr(self.receiver.max_attributes, self.attribute_modified, self.amount)

		if self.timeout > -1:
			heartbeat.attach(self)
		
	def remove(self):
		setattr(self.receiver.attributes, self.attribute_modified, -self.amount)
		setattr(self.receiver.max_attributes, self.attribute_modified, -self.amount)
	
	def tick(self):
		global heartbeat

		self.timeout -= 1
		if self.timeout < 0:
			self.remove()
			heartbeat.detach(self)

	def calculateEffectiveness(self, invoker, receiver):
		return 1

class ExtraAttack(Affect):
	def __init__(self):
		self.primary_attributes = ["dex"]

class Berserk(Affect):
	def __init__(self):
		self.primary_attributes = ["str", "dex", "con"]
		self.modifiers = [Hitroll(0.05), Damroll(0.05), Fortitude(80)]

class Hitroll(AttributeModifier):
	def __init__(self):
		self.name = "hitroll"
		self.primary_attributes = ["dex"]
		self.attribute_modified = "hit"

class Damroll(AttributeModifier):
	def __init__(self):
		self.name = "damroll"
		self.primary_attributes = ["str"]
		self.attribute_modified = "dam"

class Fortitude(AttributeModifier):
	def __init__(self):
		self.name = "fortitude"
		self.primary_attributes = ["con"]
		self.attribute_modified = "hp"
"""
