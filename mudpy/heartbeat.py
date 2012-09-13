import random, time

class Heartbeat:
	instance = None

	def __init__(self, reactor):
		self.observers = []
		self.reactor = reactor
		Heartbeat.instance = self
	
	def start(self):
		i = 0
		next_tick = 1#random.randint(10, 15)
		while(1):
			time.sleep(1)
			i += 1
			if i == next_tick:
				next_tick = 1#random.randint(10, 15)
				i = 0
				self.tick()
	
	def attach(self, observer):
		if not observer in self.observers:
			self.observers.append(observer)
	
	def detach(self, observer):
		try:
			self.observers.remove(observer)
		except ValueError:
			pass
	
	def tick(self):
		for i in self.observers:
			self.reactor.callFromThread(i.tick)
