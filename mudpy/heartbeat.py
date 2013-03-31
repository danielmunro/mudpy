import random, time
from observer import Observer
from debug import Debug
from stopwatch import Stopwatch

class Heartbeat(Observer):
	instance = None

	TICK_LOWBOUND_SECONDS = 10
	TICK_HIGHBOUND_SECONDS = 15

	PULSE_SECONDS = 1

	EVENT_TYPES = ['tick', 'pulse', 'stat', 'processCommand']

	def __init__(self, reactor):
		self.reactor = reactor
		self.stopwatch = Stopwatch()
		Heartbeat.instance = self
		super(Heartbeat, self).__init__()
		Debug.log('heartbeat created')
	
	def start(self):
		next_pulse = time.time()+Heartbeat.PULSE_SECONDS
		next_tick = time.time()+random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, Heartbeat.TICK_HIGHBOUND_SECONDS)
		while(1):
			self.dispatch('processCommand')
			if time.time() >= next_pulse:
				next_pulse += Heartbeat.PULSE_SECONDS
				self.dispatch('pulse', 'stat')
			if time.time() >= next_tick:
				next_tick = time.time()+random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, Heartbeat.TICK_HIGHBOUND_SECONDS)
				stopwatch = Stopwatch()
				self.dispatch('tick')
				Debug.log('dispatched tick ['+str(stopwatch)+'s elapsed in tick] ['+str(self.stopwatch)+'s elapsed since start]')

	def dispatch(self, *eventlist, **events):
		for event in eventlist:
			map(self.reactor.callFromThread, list(getattr(observer, event) for observer in self.observers[event]))

		for event, args in events.iteritems():
			for fn in list(getattr(observer, event) for observer in self.observers[event]):
				self.reactor.callFromThread(fn, args)
