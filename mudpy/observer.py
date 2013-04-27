"""Allows for a simple way to have objects update each other about certain
events and states without forcing the objects to be tightly coupled.

"""

class Observer(object):
	"""Any object that wants to notify other objects of state changes must
	inherit from Observer.

	"""

	def __init__(self):
		self.observers = {}

	def attach(self, event, func):
		"""Attach a new listener function to a named event."""

		try:
			self.observers[event].append(func)
		except KeyError:
			self.observers[event] = [func]
	
	def detach(self, event, func):
		"""Remove a listener function from a named event."""

		try:
			self.observers[event].remove(func)
		except (ValueError, KeyError):
			pass
	
	def dispatch(self, *eventlist, **events):
		"""Fire off one or more events, calling any found listeners."""

		handled = None

		for event in eventlist:
			try:
				for func in self.observers[event]:
					handled = func()
					if handled:
						break
			except KeyError:
				pass

		for event, args in events.iteritems():
			try:
				for func in self.observers[event]:
					handled = func(args)
					if handled:
						break
			except KeyError:
				pass

		return handled
