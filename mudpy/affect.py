from attributes import Attributes
from heartbeat import Heartbeat
from observer import Observer

class Affect(Observer):
	EVENT_TYPES = ['startAffect', 'endAffect']

	def __init__(self):
		self.name = "an affect"
		self.attributes = Attributes()
		self.timeout = 0
		self.affected = None
		super(Affect, self).__init__()
	
	def start(self):
		self.attach('startAffect', self.affected)
		self.attach('endAffect', self.affected)
		Heartbeat.instance.attach('tick', self)
		for attr in vars(self.attributes):
			modifier = getattr(self.attributes, attr)
			if modifier > 0 and modifier < 1:
				setattr(self.attributes, attr, self.affected.getAttribute(attr) * modifier)
		self.dispatch(startAffect = self)
	
	def tick(self):
		self.timeout -= 1
		if self.timeout < 0:
			Heartbeat.instance.detach('tick', self)
			self.dispatch(endAffect = self)
			self.detach('startAffect', self.affected)
			self.detach('endAffect', self.affected)

	def __str__(self):
		return self.name
