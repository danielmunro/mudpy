from . import observer
from .wireframes import race
import random

__standing__ = 'standing'
__sitting__ = 'sitting'
__laying__ = 'laying'
__sleeping__ = 'sleeping'
__incapacitated__ = 'incapacitated'
__start_room__ = 1

class Actor(observer.Observer):

    __stats__ = ['hp', 'mana', 'movement', 'luck']
    __attributes__ = ['str', 'int', 'wis', 'dex', 'con', 'cha', 'saves', 'hit', 'dam', 'hp', 'mana', 'movement', 'luck']

    def __init__(self, publisher):
        
        self.name = "traveller"
        self.short_desc = "A wandering traveller"
        self.long_desc = "A wandering traveller is here, seemingly lost."
        self.race = None
        self.room = None
        self.disposition = __standing__
        self.publisher = publisher
        self.attributes = dict((attr, 0) for attr in self.__attributes__)
        self.stats = dict((stat, 0) for stat in self.__stats__)

        super(Actor, self).__init__()

    def set_race(self, _race):
        
        if not isinstance(_race, race.Race):
            raise ValueError(str(_race)+' must be of type Race')

        self.race = _race

    def regen(self, base_percent):

        self._modify_stats(base_percent + self._get_disposition_regen_modifier())
        self._normalize_stats()

    def get_attr(self, attr):
        
        return self.attributes[attr] + self.race.attributes[attr]

    def add_to_attr(self, attr, value):

        self.attributes[attr] = self.attributes[attr] + value

        if attr in self.__stats__:
            self.stats[attr] = self.stats[attr] + value

    def _modify_stats(self, percent):
        
        for attr in self.__stats__:
            self.stats[attr] = self.stats[attr] + self.get_attr(attr) * percent

    def _normalize_stats(self):
        
        for attr in self.__stats__:
            if self.stats[attr] > self.get_attr(attr):
                self.stats[attr] = self.get_attr(attr)

    def _get_disposition_regen_modifier(self):

        d = self.disposition

        if d == __standing__ or d == __incapacitated__:
            return random.uniform(0.03, 0.08)
        elif d == __laying__ or d == __sitting__:
            return random.uniform(0.09, 0.15)
        elif diposition == __sleeping__:
            return random.uniform(0.16, 0.3)

    def _setup_events(self):
        
        def _tick(_event):
            self.regen(.1)

        self.publisher.on("tick", _tick)

    def __str__(self):
        return self.short_desc