import random, time
from observer import Observer
from debug import Debug
from stopwatch import Stopwatch

class Heartbeat(Observer):
	instance = None

	TICK_LOWBOUND_SECONDS = 10
	TICK_HIGHBOUND_SECONDS = 15

	PULSE_SECONDS = 1

	EVENT_TYPES = ['tick', 'pulse', 'stat']

	def __init__(self, reactor, stopwatch):
		self.reactor = reactor
		self.stopwatch = stopwatch
		Heartbeat.instance = self
		super(Heartbeat, self).__init__()
		Debug.log('heartbeat created')
	
	def start(self):
		i = 0
		next_tick = 0
		while(1):
			time.sleep(Heartbeat.PULSE_SECONDS)
			i += Heartbeat.PULSE_SECONDS
			self.dispatch('pulse', 'stat')
			if i > next_tick:
				next_tick = random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, Heartbeat.TICK_HIGHBOUND_SECONDS)
				stopwatch = Stopwatch()
				self.dispatch('tick')
				Debug.log('dispatched tick ['+str(stopwatch)+'s elapsed in tick] ['+str(self.stopwatch)+'s elapsed since start]')
				i = 0

	def dispatch(self, *eventlist, **events):
		for event in eventlist:
			map(self.reactor.callFromThread, list(getattr(observer, event) for observer in self.observers[event]))

		for event, args in events.iteritems():
			for fn in list(getattr(observer, event) for observer in self.observers[event]):
				self.reactor.callFromThread(fn, args)
