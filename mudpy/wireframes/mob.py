"""Mobs are creatures in the game."""
from .. import actor, wireframe
import random

class Mob(actor.Actor, wireframe.Blueprint):
    """NPCs of the game, mobs are the inhabitants of the mud world."""

    ROLE_TRAINER = 'trainer'
    ROLE_ACOLYTE = 'acolyte'

    yaml_tag = "mob"

    def __init__(self, publisher):
        self.movement = 0
        self.movement_timer = self.movement
        self.respawn = 1
        self.respawn_timer = self.respawn
        self.auto_flee = False
        self.start_room = None
        self.aggressive = False
        
        super(Mob, self).__init__(publisher)
    
    def tick(self, _event):
        super(Mob, self).tick()
        if self.movement:
            self._decrement_movement_timer()
        if self.aggressive:
            for actor in self.room.actors:
                if not actor is self:
                    self.set_target(actor)
                    break

    def actor_changed(self, event, actor, message = ""):
        if self.aggressive and actor.last_command.action == "move" and self.room.get_actor(actor):
            self.set_target(actor)
            event.handle()
    
    def _decrement_movement_timer(self):
        """Counts down to 0, at which point the mob will attempt to move from
        their current room to a new one. They cannot move to new areas however.

        """

        self.movement_timer -= 1
        if self.movement_timer < 0:
            direction = random.choice([direction for direction, _room in 
                self.room.directions.items() if _room and 
                _room.area == self.room.area])
            command.move(self, direction)
            self.movement_timer = self.movement
    
    def _normalize_stats(self, _event = None, _args = None):
        if self.curhp < 0:
            self._die()
        super(Mob, self)._normalize_stats()
    
    def _die(self):
        super(Mob, self)._die()
        self.room.move_actor(self)
        room.get(room.__config__['purgatory']).arriving(self)
        __main__.__mudpy__.on('tick', self._respawn)

    def _respawn(self):
        self.respawn_timer -= 1
        if self.respawn_timer < 0:
            __main__.__mudpy__.off('tick', self._respawn)
            self.disposition = disposition.__standing__
            self.curhp = self.get_attribute('hp')
            self.curmana = self.get_attribute('mana')
            self.curmovement = self.get_attribute('movement')
            self.room.move_actor(self)
            room.get(self.start_room).arriving(self)
