from attributes import Attributes
from heartbeat import Heartbeat
from actor import User

class Affect(object):
	def __init__(self):
		self.name = "an affect"
		self.msgYouWearOff = ""
		self.msgRoomWearOff = ""
		self.attributes = Attributes()
		self.timeout = 0
		self.affected = None
	
	def start(self):
		Heartbeat.instance.attach('tick', self)
		self.affected.affects.append(self)
		for attr in vars(self.attributes):
			modifier = getattr(self.attributes, attr)
			if modifier > 0 and modifier < 1:
				setattr(self.attributes, attr, self.affected.getAttribute(attr) * modifier)
	
	def end(self):
		Heartbeat.instance.detach('tick', self)
		self.affected.affects.remove(self)
		if isinstance(self.affected, User) and self.msgYouWearOff:
			self.affected.notify(self.msgYouWearOff+"\n"+self.affected.prompt())
	
	def tick(self):
		self.timeout -= 1
		if self.timeout < 0:
			self.end()

	def __str__(self):
		return self.name
