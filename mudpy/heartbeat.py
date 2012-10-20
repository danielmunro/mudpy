import random, time

class Heartbeat:
	instance = None

	TICK_LOWBOUND_SECONDS = 10
	TICK_HIGHBOUND_SECONDS = 15

	PULSE_SECONDS = 1

	EVENT_TYPES = ['tick', 'pulse', 'stat']

	def __init__(self, reactor):
		self.observers = dict((event, []) for event in Heartbeat.EVENT_TYPES)
		self.reactor = reactor
		Heartbeat.instance = self
	
	def start(self):
		i = 0
		next_tick = 0
		while(1):
			time.sleep(Heartbeat.PULSE_SECONDS)
			i += Heartbeat.PULSE_SECONDS
			self.dispatch('pulse')
			self.dispatch('stat')
			if i > next_tick:
				next_tick = self.getTickLength()
				self.dispatch('tick')
				i = 0
	
	def attach(self, event, observer):
		if not observer in self.observers[event]:
			self.observers[event].append(observer)
	
	def detach(self, event, observer):
		try:
			self.observers[event].remove(observer)
		except ValueError:
			pass

	def dispatch(self, event):
		map(self.reactor.callFromThread, list(getattr(observer, event) for observer in self.observers[event]))

	def getTickLength(self):
		return random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, Heartbeat.TICK_HIGHBOUND_SECONDS);
