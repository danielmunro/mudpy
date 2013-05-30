"""Affect has a set of attributes and an optional timeout. These are intended
to be used to apply attribute changes to an actor or item.

"""

from . import debug, server, room, attributes, observer

class Affect(observer.Observer, room.Reporter):
    """Give an actor or item an affect."""

    def __init__(self):
        self.name = "an affect"
        self.attributes = attributes.Attributes()
        self.timeout = 0
        self.messages = {}
        super(Affect, self).__init__()
    
    def set_attributes_from_receiver(self, receiver):
        """Calculate modifiers that are percentages of an attribute of the
        receiver.
        
        """

        # for any modifiers that are percents, we need to 
        # get the percent of the receiver's attribute
        for attr in vars(self.attributes):
            modifier = getattr(self.attributes, attr)
            if modifier > 0 and modifier < 1:
                setattr(self.attributes, attr, receiver.get_attribute(attr)
                        * modifier)

    def countdown_timeout(self):
        """Count down the affect timer."""

        self.timeout -= 1
        if self.timeout < 0:
            server.__instance__.heartbeat.detach('tick', self.countdown_timeout)
            self.dispatch('end')

    def __str__(self):
        return self.name
