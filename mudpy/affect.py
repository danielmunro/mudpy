"""Affect has a set of attributes and an optional timeout. These are intended
to be used to apply attribute changes to an actor or item.

"""

from . import debug, server, room, observer

class Affect(observer.Observer, room.Reporter):
    """Give an actor or item an affect."""

    def __init__(self):
        self.name = "an affect"
        self.attributes = {}
        self.timeout = 0
        self.messages = {}

    def get_attribute(self, attr):
        try:
            return self.attributes[attr]
        except KeyError:
            return 0
    
    def countdown_timeout(self):
        """Count down the affect timer."""

        self.timeout -= 1
        if self.timeout < 0:
            server.__instance__.heartbeat.detach('tick', self.countdown_timeout)
            self.dispatch('end', affect=self)

    def __str__(self):
        return self.name
