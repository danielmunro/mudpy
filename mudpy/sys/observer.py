"""Allows for a simple way to have objects update each other about certain
events and states without forcing the objects to be tightly coupled.

"""

def fire_events(event, listeners):
    """Call a list of listeners and pass the given event to them."""
    for fn in listeners:
        try:
            fn(event, *event.args)
        except(EventBreakoutException):
            break

class Observer(object):
    """Any object that wants to notify other objects of state changes must
    inherit from Observer.

    """

    def __init__(self):
        self.observers = {}

    def on(self, event, fn):
        """Attach a new listener function to a named event."""

        if not event in self.observers:
            self.observers[event] = []

        self.observers[event].append(fn)
    
    def off(self, event, fn):
        """Remove a listener function from a named event."""

        if event in self.observers:
            self.observers[event].remove(fn)
    
    def fire(self, event_name, *args):
        """Fire off an event, calling any found listeners."""

        event_name = str(event_name)
        event = Event(event_name, self, args)

        if event_name in self.observers:
            fire_events(event, self.observers[event_name])

        if "__any__" in self.observers:
            fire_events(event, self.observers["__any__"])

        if not event.handled and not event_name.endswith("__unhandled__"):
            return self.fire(event_name+".__unhandled__", *args)
        else:
            return event.handled

class Event:
    """Convenient object to encapsulate the state of a fired event."""

    def __init__(self, name, publisher, args):
        self.name = name
        self.publisher = publisher
        self.args = args
        self.handled = False

    def handle(self):
        """Used to break out of an event loop by the observer/publisher."""
        self.handled = True
        raise EventBreakoutException()

    def __str__(self):
        return self.name

class EventBreakoutException(Exception):
    """Observer wraps this exception in a try/catch, so it is useful for
    breaking out of event loops if the nature of the event is that it can be
    handled by a listener.

    """

    pass
