class Observer(object):
	observers = {}
	EVENT_TYPES = []

	def __init__(self):
		if len(self.EVENT_TYPES) == 0:
			raise ObserverException("observer must define at least one event type in EVENT_TYPES")
		self.observers = dict((event, []) for event in self.EVENT_TYPES)

	def attach(self, event, observer):
		try:
			if not observer in self.observers[event]:
				self.observers[event].append(observer)
		except KeyError:
			# observer doesn't support this type of event... technically bug
			pass
	
	def detach(self, event, observer):
		try:
			self.observers[event].remove(observer)
		except ValueError:
			# observer is not actually an observer
			pass
	
	def dispatch(self):
		raise("dispatch() not defined in observer")

class ObserverException(Exception): pass
