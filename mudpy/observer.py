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

        if not event in self.observers:
            self.observers[event] = []

        self.observers[event].append(func)
    
    def detach(self, event, func):
        """Remove a listener function from a named event."""

        if event in self.observers:
            self.observers[event].remove(func)
    
    def dispatch(self, event, *args):
        """Fire off an event, calling any found listeners."""

        handled = None

        if event in self.observers:
            for func in self.observers[event]:
                handled = func(*args)
                if handled:
                    break

        if "__any__" in self.observers:
            for func in self.observers["__any__"]:
                handled = func(event, *args)
                if handled:
                    break

        return handled
