"""Rooms in a mud represent the physical space in which the creatures, mobs,
items, and players occupy. They can be towns, trails, forests, mines, oceans,
dungeons, and more.

"""

from ..sys import wireframe, collection, debug
from . import item
import random

__rooms__ = {}
__areas__ = {}
__config__ = wireframe.create("config.room")
__auto_room_name__ = 1

__LOCATION_OUTSIDE__ = "outside"

def auto_room_name():
    global __auto_room_name__
    while __auto_room_name__ in __rooms__:
        __auto_room_name__ = __auto_room_name__ + 1
    return __auto_room_name__


def get(room_name, direction = ""):
    _room = __rooms__[room_name]
    if direction:
        if direction in _room.directions:
            _room = _room.directions[direction]
        else:
            _room = None
    return _room

def area(area_name):
    return __areas__[area_name]

def copy(start_room, direction):
    # create new room
    new_room = Room()
    new_room.short_desc = start_room.short_desc
    new_room.long_desc = start_room.long_desc
    new_room.area = start_room.area
    new_room.lit = start_room.lit
    new_room.name = auto_room_name()
    new_room.directions[Direction.get_reverse(direction)] = start_room.name
    start_room.directions[direction] = new_room.name

    __rooms__[new_room.name] = new_room
    start_room.get_area().rooms.append(new_room)
    return new_room

class Room(wireframe.Blueprint):
    """Basic space representation game configuration files. Has a name (title),
    description, a list of actors in the room, an inventory of items, and a
    dictionary of possible directions to leave.

    """

    yaml_tag = "u!room"

    def __init__(self):
        self.actors = []
        self.inventory = item.Inventory()
        self.directions = {}
        self.area = ''
        self.lit = True
        super(Room, self).__init__()

    def done_init(self):
        from . import actor
        for mob in self.mobs():
            actor.actor.__proxy__.fire("actor_enters_realm", mob)
            self.arriving(mob)
            mob.start_room = self.name

    def get_area(self):
        return area(self.area)

    def get_actor(self, name):
        return collection.find(name, self.actors)
    
    def announce(self, messages, add_prompt = True):
        """Will take a message and convey it to the various actors in the
        room. Any updates at the room level will be broadcasted through
        here.

        """

        announcedActors = []
        generalMessage = ""
        for actor, message in messages.iteritems():
            if actor == "all":
                generalMessage = message
            else:
                if message:
                    actor.notify(message = message, add_prompt = add_prompt)
                announcedActors.append(actor)
        if generalMessage:
            for actor in list(set(self.actors) - set(announcedActors)):
                actor.notify(generalMessage, add_prompt)
    
    def mobs(self):
        from actor.mob import Mob
        return list(actor for actor in self.actors if isinstance(actor, Mob))

    def _copy(self, newRoom):
        newRoom.name = self.name
        newRoom.short_desc = self.short_desc
        newRoom.long_desc = self.long_desc
        newRoom.area = self.area
        for direction in Direction.get_all():
            if not direction.name in self.directions:
                self.directions[direction.name] = None
        return newRoom

    def move_actor(self, actor, direction = None):
        if actor in self.actors:
            self.leaving(actor, direction)
            if direction:
                new_room = get(self.directions[direction])
                debug.log(str(actor)+" moves to "+new_room.short_desc+\
                        " ("+str(new_room.name)+")")
                new_room.arriving(actor, Direction.get_reverse(direction))

    def leaving(self, actor, direction = ""):
        handled = self.fire("leaving", actor)
        self.off("actor_changed", actor.actor_changed)
        if not handled:
            self.actors.remove(actor)

    def arriving(self, actor, direction = ""):
        handled = self.fire("arriving", actor)
        self.on("actor_changed", actor.actor_changed)
        if not handled:
            if not actor in self.actors:
                self.actors.append(actor)
            actor.room = self.name
    
    @classmethod
    def to_yaml(self, dumper, thing):
        from .actor import mob
        import copy
        persist = copy.copy(thing)
        persist.actors = [i for i in persist.actors if isinstance(i, mob.Mob)]
        return super(Room, self).to_yaml(dumper, persist)

    def __str__(self):
        return str(self.name)

class Dungeon(wireframe.Blueprint):

    yaml_tag = "u!dungeon"

    def __init__(self):
        self.exits = []
        self.size = 0
        self.lit = False
        self.directions = {}

    def done_init(self):
        self.room = Room()
        self.room.name = self.name
        self.room.short_desc = self.short_desc
        self.room.long_desc = self.long_desc
        self.room.area = self.area
        self.room.directions = self.directions
        __rooms__[self.room.name] = self.room
        self.room.get_area().rooms.append(self.room)
        self._build_dungeon()
    
    def _build_dungeon(self, existing_room = None, room_count = 1):
        if room_count < self.size:
            origin_room = existing_room if existing_room else self.room
            used_directions = origin_room.directions.keys()
            if random.random() < self.branching:
                available_directions = list(direction.name for direction in Direction.get_all() if not direction.name in used_directions)
                if available_directions:
                    random_direction = random.choice(available_directions)
                    branching_room = copy(origin_room, random_direction)
                    return self._build_dungeon(origin_room, room_count + 1)
                else:
                    return self._build_dungeon(get(origin_room.directions[random.choice(list(direction.name for direction in Direction.get_all()))]), room_count)
            else:
                branching_room = copy(origin_room, self._get_random_direction(origin_room))
                return self._build_dungeon(branching_room, room_count + 1)

    def _get_random_direction(self, origin_room):
        toss = random.random()
        counter = 0
        while 1:
            for i in self.probabilities:
                counter = counter + self.probabilities[i]
                if toss < counter and i not in origin_room.directions:
                    return i

class Grid(Room):
    def __init__(self):
        super(Grid, self).__init__()
        self.counts = {}
        self.exit = 0
    
    def buildDungeon(self, x = 0, y = 0, grid = []):
        ylen = len(grid)
        xlen = len(grid[0])
        for y in range(ylen):
            for x in range(xlen):
                if not isinstance(grid[y][x], Grid):
                    grid[y][x] = self._copy()
                if x > 0:
                    grid[y][x-1].setIfEmpty('east', grid[y][x])
                if y > 0:
                    grid[y-1][x].setIfEmpty('south', grid[y][x])
        exit = self.exit
        while exit:
            rand_x = int(round(random.random()*xlen))-1
            rand_y = int(round(random.random()*ylen))-1
            direction = Direction.get_random()
            if not grid[rand_y][rand_x].directions[direction]:
                room_key = self.area.name+":"+str(exit)
                grid[rand_y][rand_x].directions[direction] = __rooms__[room_key]
                class_name = direction.title()
                __rooms__[room_key].directions[globals()[class_name].reverse]=\
                                                        grid[rand_y][rand_x]
                exit = None
    
    def setIfEmpty(self, direction, roomToSet):
        rdir = globals()[direction.title()].reverse
        if self.directions[direction] is None:
            self.directions[direction] = roomToSet
            if roomToSet.directions[rdir] is None:
                roomToSet.directions[rdir] = self


    def _copy(self):
        r = super(Grid, self)._copy(Grid())
        r.exit = self.exit
        r.counts = self.counts
        return r

class Direction(object):
    name = ""

    @staticmethod
    def get_all():
        return Direction.__subclasses__()

    @staticmethod
    def match(direction):
        for _direction in ["north", "south", "east", "west", "up", "down"]:
            if _direction.startswith(direction):
                return _direction
    
    @staticmethod
    def get_random(allowed_directions = []):
        return random.choice(allowed_directions if allowed_directions else \
            list(direction.name for direction in Direction.get_all()))

    @staticmethod
    def get_reverse(direction):
        return globals()[direction.title()].reverse

class North(Direction):
    name = "north"
    reverse = "south"

class South(Direction):
    name = "south"
    reverse = "north"

class East(Direction):
    name = "east"
    reverse = "west"

class West(Direction):
    name = "west"
    reverse = "east"

class Up(Direction):
    name = "up"
    reverse = "down"

class Down(Direction):
    name = "down"
    reverse = "up"

class Area(wireframe.Blueprint):

    yaml_tag = "u!area"

    def __init__(self):
        self.terrain = ""
        self.location = ""
        self.rooms = []
        super(Area, self).__init__()

    def done_init(self):
        from . import actor
        __areas__[self.name] = self
        for room in self.rooms:
            __rooms__[room.name] = room
            room.area = self.name
            room.done_init()

    def __str__(self):
        return self.name
