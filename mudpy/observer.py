from debug import Debug

class Observer(object):
	observers = {}
	EVENT_TYPES = []

	def __init__(self):
		if len(self.EVENT_TYPES) == 0:
			Debug.log("observer must define at least one event type in EVENT_TYPES", "error")
		self.observers = dict((event, []) for event in self.EVENT_TYPES)

	def attach(self, event, observer):
		try:
			self.observers[event].append(observer)
		except KeyError:
			Debug.log("Observer "+str(observer)+" does not support event type: "+str(event), "error")
	
	def detach(self, event, observer):
		try:
			self.observers[event].remove(observer)
		except ValueError:
			Debug.log("Observer not actually observing: "+str(observer), "notice")
	
	def dispatch(self, *eventlist, **events):
		for event in eventlist:
			list(getattr(observer, event)() for observer in self.observers[event])

		for event, args in events.iteritems():
			for fn in list(getattr(observer, event) for observer in self.observers[event]):
				fn(args)
