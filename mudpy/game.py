from . import wireframe
import importlib, __main__

__instance__ = None

if '__mudpy__' in __main__.__dict__:

    def initialize():
        global __instance__
        __instance__ = wireframe.create("game")
        __instance__.setup_events()

    __main__.__mudpy__.attach("initialize", initialize)

class Game(wireframe.Blueprint):

    yaml_tag = "u!game"

    def __init__(self):
        self.observers = {}
        self.events = {}

    def setup_events(self):
        for e in self.events:
            __main__.__mudpy__.attach(e, self.attach_event)

    def attach_event(self, event, observer):
        event_names = self.events[event]
        for event_name in event_names:
            fn = getattr(observer, event_name[1])
            __main__.__mudpy__.attach(event_name[0], fn)
