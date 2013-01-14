import random, time
from observer import Observer

class Heartbeat(Observer):
	instance = None

	TICK_LOWBOUND_SECONDS = 10
	TICK_HIGHBOUND_SECONDS = 15

	PULSE_SECONDS = 1

	EVENT_TYPES = ['tick', 'pulse', 'stat']

	def __init__(self, reactor):
		self.reactor = reactor
		Heartbeat.instance = self
		super(Heartbeat, self).__init__()
	
	def start(self):
		i = 0
		next_tick = 0
		while(1):
			time.sleep(Heartbeat.PULSE_SECONDS)
			i += Heartbeat.PULSE_SECONDS
			self.dispatch('pulse', 'stat')
			if i > next_tick:
				next_tick = self.getTickLength()
				self.dispatch('tick')
				i = 0
	
	def getTickLength(self):
		return random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, Heartbeat.TICK_HIGHBOUND_SECONDS);

	def dispatch(self, *events):
		for event in events:
			map(self.reactor.callFromThread, list(getattr(observer, event) for observer in self.observers[event]))
