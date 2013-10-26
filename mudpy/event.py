from . import wireframe
import __main__

class Event(wireframe.Blueprint):

    yaml_tag = "u!event"

    def __init__(self):
        self.observers = {}
        self.events = {}

    def setup_events(self):
        for e in self.events:
            __main__.__mudpy__.attach(e, self.attach_event)

    def attach_event(self, event, observer):
        event_names = self.events[event]
        for event_name in event_names:
            fn = getattr(observer, event_name)
            __main__.__mudpy__.attach(event_name, fn)
