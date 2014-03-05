from . import observer, mud, wireframes
import random

__standing__ = 'standing'
__sitting__ = 'sitting'
__laying__ = 'laying'
__sleeping__ = 'sleeping'
__incapacitated__ = 'incapacitated'

class Actor(observer.Observer):

    __stats__ = ['hp', 'mana', 'movement', 'luck']
    __attributes__ = ['str', 'int', 'wis', 'dex', 'con', 'cha', 'saves', 'hit', 'dam', 'hp', 'mana', 'movement', 'luck']
    
    def __init__(self):
        
        self.race = None
        self.room = None
        self.disposition = __standing__
        self.attributes = dict((attr, 0) for attr in self.__attributes__)
        self.current_stats = dict((stat, 0) for stat in self.__stats__)

        super(Actor, self).__init__()

    def set_race(self, race):
        
        if not isinstance(race, wireframes.race.Race):
            raise ValueError(str(race)+' must be of type Race')

        self.race = race

    def regen(self, base_percent):

        self._modify_stats(base_percent + self._get_disposition_regen_modifier())
        self._normalize_stats()

    def get_attr(self, attr):
        
        return self.attributes[attr] + self.race.attributes[attr]

    def _modify_stats(self, percent):
        
        for attr in self.__stats__:
            self.current_stats[attr] = self.current_stats[attr] + self.get_attr(attr) * percent

    def _normalize_stats(self):
        
        for attr in self.__stats__:
            if self.current_stats[attr] > self.get_attr(attr):
                self.current_stats[attr] = self.get_attr(attr)

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

        mud.__self__.on("tick", self._tick)