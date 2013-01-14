class Observer(object):
	observers = {}
	EVENT_TYPES = []

	def __init__(self):
		if len(self.EVENT_TYPES) == 0:
			raise ObserverException("observer must define at least one event type in EVENT_TYPES")
		self.observers = dict((event, []) for event in self.EVENT_TYPES)

	def attach(self, event, observer):
		if not observer in self.observers[event]:
			self.observers[event].append(observer)
	
	def detach(self, event, observer):
		try:
			self.observers[event].remove(observer)
		except ValueError:
			pass

	def dispatch(self, *events):
		raise ObserverException("no dispatch() defined in observer")

class ObserverException(Exception): pass
