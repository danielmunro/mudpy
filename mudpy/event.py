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
                else:
                    fn = eval('self.publisher.'+listeners['method'])
                    self.publisher.on(e, fn)

    def register_subscriber_to_publisher(self, event, subscriber):
        for e in self.events[event]:
            if 'add_subscriber_callback' in e:
                subscriber_callback = e['add_subscriber_callback']
                fn = getattr(subscriber, subscriber_callback)
                self.publisher.on(e['event'], fn)
            elif 'remove_subscriber_callback' in e:
                subscriber_callback = e['remove_subscriber_callback']
                fn = getattr(subscriber, subscriber_callback)
                self.publisher.off(e['event'], fn)

    def execute(self, event, subscriber, *_args):
        for e in self.events[event]:
            if 'execute' in e:
                eval('subscriber.'+e['execute'])

    def proxy(self, event, subscriber, *args):
        success = False
        for e in self.events[event]:
            if 'proxy' in e:
                callback = eval('self.publisher.'+e['proxy'])
                success = callback(event, subscriber, *args)
        return success

    def off(self, event, subscriber, *args):
        for e in self.events[event]:
            if 'off' in e:
                for inner_e in self.events[e['off']]:
                    if 'proxy' in inner_e:
                        subscriber.off(e['off'], self.proxy)
