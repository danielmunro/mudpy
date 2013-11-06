from . import wireframe
import __main__

class Event(wireframe.Blueprint):

    yaml_tag = "u!event"

    def __init__(self):
        self.observers = {}
        self.events = {}

    def setup(self, publisher):
        self.publisher = publisher
        for e in self.events:
            for fn in self.events[e]:
                self.publisher.on(e, getattr(self, fn))
        return self

    def register(self, event, subscriber):
        fn = self.events[event]['register']
        self.publisher.on(fn, getattr(subscriber, fn))

    def unregister(self, event, subscriber):
        fn = self.events[event]['unregister']
        self.publisher.off(fn, getattr(subscriber, fn))

    def proxy(self, event, subscriber, *args):
        callback = eval('self.publisher.'+self.events[event]['proxy'])
        return callback(event, subscriber, *args)

    def off(self, event, subscriber, *args):
        e_off = self.events[event]['off']
        for fn in self.events[e_off]:
            self.publisher.off(e_off, getattr(self, fn))