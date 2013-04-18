import random, time
import debug
from observer import Observer
from stopwatch import Stopwatch

class Heartbeat(Observer):
	instance = None

	TICK_LOWBOUND_SECONDS = 10
	TICK_HIGHBOUND_SECONDS = 15

	PULSE_SECONDS = 1

	def __init__(self, reactor):
		self.reactor = reactor
		self.stopwatch = Stopwatch()
		Heartbeat.instance = self
		super(Heartbeat, self).__init__()
		debug.log('heartbeat created')
	
	def start(self):
		next_pulse = time.time()+Heartbeat.PULSE_SECONDS
		next_tick = time.time()+random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, Heartbeat.TICK_HIGHBOUND_SECONDS)
		while(1):
			self.dispatch('cycle')
			if time.time() >= next_pulse:
				next_pulse += Heartbeat.PULSE_SECONDS
				self.dispatch('pulse', 'stat')
			if time.time() >= next_tick:
				next_tick = time.time()+random.randint(Heartbeat.TICK_LOWBOUND_SECONDS, Heartbeat.TICK_HIGHBOUND_SECONDS)
				stopwatch = Stopwatch()
				self.dispatch('tick')
				debug.log('dispatched tick ['+str(stopwatch)+'s elapsed in tick] ['+str(self.stopwatch)+'s elapsed since start]')

	def dispatch(self, *eventlist, **events):
		for event in eventlist:
			try:
				map(self.reactor.callFromThread, list(fn for fn in self.observers[event]))
			except KeyError: pass

		for event, args in events.iteritems():
			for fn in self.observers[event]:
				self.reactor.callFromThread(fn, args)
