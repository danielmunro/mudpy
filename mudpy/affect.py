"""Affect has a set of attributes and an optional timeout. These are intended
to be used to apply attribute changes to an actor or item.

"""

from attributes import Attributes
from observer import Observer
from reporter import Reporter
from . import debug, heartbeat

class Affect(Observer, Reporter):
	"""Give an actor or item an affect."""

	def __init__(self):
		self.name = "an affect"
		self.attributes = Attributes()
		self.timeout = 0
		self.messages = {}
		super(Affect, self).__init__()
	
	def start(self, receiver):
		"""Apply the affect to a receiver."""

		try:
			self.attach('start', receiver.startAffect)
			self.attach('end', receiver.endAffect)
		except AttributeError:
			debug.log(str(receiver)+
				" does not have startAffect() and/or endAffect() defined",
				"error")
		heartbeat.instance.attach('tick', self.tick)
		self.set_attributes_from_receiver(receiver)
		self.dispatch(start = self)
	
	def set_attributes_from_receiver(self, receiver):
		"""Calculate modifiers that are percentages of an attribute of the
		receiver.
		
		"""

		# for any modifiers that are percents, we need to 
		# get the percent of the receiver's attribute
		for attr in vars(self.attributes):
			modifier = getattr(self.attributes, attr)
			if modifier > 0 and modifier < 1:
				setattr(self.attributes, attr, receiver.getAttribute(attr)
						* modifier)
	
	def tick(self):
		"""Tick listener, count down and remove affect."""

		self.timeout -= 1
		if self.timeout < 0:
			heartbeat.instance.detach('tick', self.tick)
			self.dispatch(end = self)

	def __str__(self):
		return self.name
