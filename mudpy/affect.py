from attributes import Attributes
from heartbeat import Heartbeat
from observer import Observer

class Affect(Observer):
	EVENT_TYPES = ['end']

	def __init__(self):
		self.name = "an affect"
		self.attributes = Attributes()
		self.timeout = 0
		self.affected = None
		self.ability = None
		super(Affect, self).__init__()
	
	def start(self):
		Heartbeat.instance.attach('tick', self)
		self.affected.affects.append(self)
		self.attach('end', self.affected)
		for attr in vars(self.attributes):
			modifier = getattr(self.attributes, attr)
			if modifier > 0 and modifier < 1:
				setattr(self.attributes, attr, self.affected.getAttribute(attr) * modifier)
	
	def tick(self):
		self.timeout -= 1
		if self.timeout < 0:
			Heartbeat.instance.detach('tick', self)
			self.dispatch(end = self)

	def __str__(self):
		return self.name
