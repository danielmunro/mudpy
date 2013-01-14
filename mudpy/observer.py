class Observer(object):
	observers = {}
	EVENT_TYPES = []

	def __init__(self):
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
		print "no dispatch() defined in observer"
		raise
