from . import wireframe
import __main__

class Event(wireframe.Blueprint):

    yaml_tag = "u!event"

    def __init__(self):
        self.observers = {}
        self.events = {}

    def on_events(self, publisher):
        self.publisher = publisher
        for e in self.events:
            for listeners in self.events[e]:
                if 'proxy' in listeners:
                    self.publisher.on(e, self.proxy)
                elif 'off' in listeners:
                    self.publisher.on(e, self.off)
                elif 'execute' in listeners:
                    self.publisher.on(e, self.execute)
                elif 'unregister' in listeners:
                    self.publisher.on(e, self.unregister)
                elif 'register' in listeners:
                    self.publisher.on(e, self.register)

    def register(self, event, subscriber):
        fn = self.events[event]['register']
        self.publisher.on(fn, getattr(subscriber, fn))

    def unregister(self, event, subscriber):
        fn = self.events[event]['unregister']
        self.publisher.off(fn, getattr(subscriber, fn))

    def execute(self, event, subscriber, *_args):
        for e in self.events[event]:
            if 'execute' in e:
                eval('subscriber.'+e['execute'])

    def proxy(self, event, subscriber, *args):
        callback = eval('self.publisher.'+self.events[event]['proxy'])
        return callback(event, subscriber, *args)

    def off(self, event, subscriber, *args):
        e_off = self.events[event]['off']
        for key in self.events[e_off]:
            if key == 'proxy':
                self.publisher.off(e_off, self.proxy)
