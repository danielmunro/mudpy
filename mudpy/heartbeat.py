import random, time

class Heartbeat:
	instance = None

	TICK_LOWBOUND_SECONDS = 10
	TICK_HIGHBOUND_SECONDS = 15

	PULSE_SECONDS = 1

	EVENT_TYPES = ['tick', 'pulse']

	def __init__(self, reactor):
		self.observers = dict((e, []) for e in Heartbeat.EVENT_TYPES)
		self.reactor = reactor
		Heartbeat.instance = self
	
	def start(self):
		i = 0
		next_tick = self.getTickLength()
		while(1):
			time.sleep(Heartbeat.PULSE_SECONDS)
			i += Heartbeat.PULSE_SECONDS
			if i > next_tick:
				next_tick = self.getTickLength()
				i = 0
				self.tick()
	
	def attach(self, event, observer):
		if not observer in self.observers:
			self.observers[event].append(observer)
	
	def detach(self, event, observer):
		try:
			self.observers[event].remove(observer)
		except ValueError:
			pass
	
	def tick(self):
		for i in self.observers['tick']:
			self.reactor.callFromThread(i.tick)
	
	def getTickLength(self):
		return random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, Heartbeat.TICK_HIGHBOUND_SECONDS);
