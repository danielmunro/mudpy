"""Affect has a set of attributes and an optional timeout. These are intended
to be used to apply attribute changes to an actor or item.

"""

from . import debug, server, room, attributes, observer, wireframe

class Affect(wireframe.Blueprint, room.Reporter):
    """Give an actor or item an affect."""

    def __init__(self, properties):
        self.name = "an affect"
        self.attributes = attributes.Attributes()
        self.timeout = 0
        self.messages = {}
        super(Affect, self).__init__(**properties)
    
    def countdown_timeout(self):
        """Count down the affect timer."""

        self.timeout -= 1
        if self.timeout < 0:
            server.__instance__.heartbeat.detach('tick', self.countdown_timeout)
            self.dispatch('end', affect=self)

    def __str__(self):
        return self.name
