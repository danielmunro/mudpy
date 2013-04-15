from attributes import Attributes
from heartbeat import Heartbeat
from observer import Observer
from reporter import Reporter

class Affect(Observer, Reporter):

	def __init__(self):
		self.name = "an affect"
		self.attributes = Attributes()
		self.timeout = 0
		self.messages = {}
		super(Affect, self).__init__()
	
	def start(self, receiver):
		self.attach('start', receiver.startAffect)
		self.attach('end', receiver.endAffect)
		Heartbeat.instance.attach('tick', self.tick)
		self.setAttributesFromReceiver(receiver)
		self.dispatch(start = self)
	
	def setAttributesFromReceiver(self, receiver):
		# for any modifiers that are percents, we need to 
		# get the percent of the receiver's attribute
		for attr in vars(self.attributes):
			modifier = getattr(self.attributes, attr)
			if modifier > 0 and modifier < 1:
				setattr(self.attributes, attr, receiver.getAttribute(attr) * modifier)
	
	def tick(self):
		self.timeout -= 1
		if self.timeout < 0:
			Heartbeat.instance.detach('tick', self.tick)
			self.dispatch(end = self)

	def __str__(self):
		return self.name
