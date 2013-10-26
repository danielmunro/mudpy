from . import wireframe
import __main__

class Event(wireframe.Blueprint):

    yaml_tag = "u!event"

    def __init__(self):
        self.observers = {}
        self.events = {}

    def setup_events(self, publisher):
        self.publisher = publisher
        for e in self.events:
            self.publisher.attach(e, self.attach_event)

    def attach_event(self, event, subscriber):
        event_names = self.events[event]
        for event_name in event_names:
            fn = getattr(subscriber, event_name)
            self.publisher.attach(event_name, fn)
