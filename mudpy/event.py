from . import wireframe
import __main__

class Event(wireframe.Blueprint):

    yaml_tag = "u!event"

    def __init__(self):
        self.observers = {}
        self.events = {}

    def attach_events(self, publisher):
        self.publisher = publisher
        for e in self.events:
            for listeners in self.events[e]:
                fn = getattr(self, listeners['method'])
                self.publisher.attach(e, fn)

    def register_subscriber_to_publisher(self, event, subscriber):
        for e in self.events[event]:
            subscriber_callback = e['subscriber_callback']
            fn = getattr(subscriber, subscriber_callback)
            self.publisher.attach(subscriber_callback, fn)
