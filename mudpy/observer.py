class Observer(object):

	def __init__(self):
		self.observers = {}

	def attach(self, event, fn):
		try:
			self.observers[event].append(fn)
		except KeyError:
			self.observers[event] = [fn]
	
	def detach(self, event, fn):
		try:
			self.observers[event].remove(fn)
		except (ValueError, KeyError): pass
	
	def detachAll(self, *args):
		self.observers.clear()
	
	def dispatch(self, *eventlist, **events):
		for event in eventlist:
			try:
				for fn in self.observers[event]:
					handled = fn()
					if handled:
						break
			except KeyError: pass

		for event, args in events.iteritems():
			try:
				for fn in self.observers[event]:
					handled = fn(args)
					if handled:
						break
			except KeyError: pass
		return handled
