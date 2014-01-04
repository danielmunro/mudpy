"""Affect has a set of attributes and an optional timeout. These are intended
to be used to apply attribute changes to an actor or item.

"""

from ..sys import wireframe
import __main__

class Affect(wireframe.Blueprint):
    """Give an actor or item an affect."""

    yaml_tag = "u!affect"

    def __init__(self):
        self.attributes = {}
        self.timeout = 0
        self.messages = {}

    def get_attribute(self, attr):
        return self.attributes[attr] if attr in self.attributes else 0
    
    def countdown_timeout(self, _event = None):
        """Count down the affect timer."""

        self.timeout -= 1
        if self.timeout < 0:
            __main__.__mudpy__.off('tick', self.countdown_timeout)
            self.fire('end', self)

    def __str__(self):
        return self.name
