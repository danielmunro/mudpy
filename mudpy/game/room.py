"""Rooms in a mud represent the physical space in which the creatures, mobs,
items, and players occupy. They can be towns, trails, forests, mines, oceans,
dungeons, and more.

"""

from ..sys import wireframe, collection
from . import item
import random

__rooms__ = {}
__areas__ = {}
__config__ = wireframe.create("config.room")

__LOCATION_OUTSIDE__ = "outside"

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
    Area.auto_room_name = Area.auto_room_name + 1

    # create new room
    new_room = Room()
    new_room.title = start_room.title
    new_room.description = start_room.description
    new_room.area = start_room.area
    new_room.lit = start_room.lit
    new_room.name = Area.auto_room_name
    new_room.directions[Direction.get_reverse(direction)] = start_room.name
    start_room.directions[direction] = new_room.name

    __rooms__[new_room.name] = new_room
    start_room.get_area().rooms.append(new_room)

class Room(wireframe.Blueprint):
    """Basic space representation game configuration files. Has a name (title),
    description, a list of actors in the room, an inventory of items, and a
    dictionary of possible directions to leave.

    """

    yaml_tag = "u!room"

    def __init__(self):
        self.name = 0
        self.title = ''
        self.description = ''
        self.actors = []
        self.inventory = item.Inventory()
        self.directions = {}
        self.area = ''
        self.lit = True
        super(Room, self).__init__()

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

    def copy(self, newRoom):
        newRoom.name = self.name
        newRoom.description = self.description
        newRoom.area = self.area
        newRoom.initialize_directions()
        return newRoom

    def initialize_directions(self):
        for direction in Direction.__subclasses__():
            try:
                self.directions[direction.name]
            except KeyError:
                self.directions[direction.name] = None

    def move_actor(self, actor, direction = None):
        if actor in self.actors:
            self.leaving(actor, direction)
            if direction:
                new_room = get(self.directions[direction])
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
        from . import actor
        import copy
        persist = copy.copy(thing)
        persist.actors = [i for i in persist.actors if isinstance(i, actor.Mob)]
        return super(Room, self).to_yaml(dumper, persist)

    def __str__(self):
        return str(self.name)

class Randomhall(Room):
    def __init__(self):
        super(Randomhall, self).__init__()
        self.rooms = 0
        self.exit = 0
        self.probabilities = \
                dict((direction, .5) for direction in self.directions)
    
    def buildDungeon(self, roomCount = 0):
        direction = Direction.get_random(list(direction \
                for direction, room in self.directions.iteritems() if not room))
        if self.probabilities[direction] > random.random():
            if self.rooms < roomCount:
                exit = __rooms__[self.area.name+":"+str(self.exit)]
                self.directions[direction] = exit
                exit.directions[globals()[direction.title()]().reverse] = self
            else:
                return self.copy(direction).buildDungeon(roomCount+1)
        else:
            rooms = list(room for room in self.directions.values() if \
                                            isinstance(room, Randomhall))
            if rooms:
                return random.choice(rooms).buildDungeon(roomCount)
        return roomCount
    
    def copy(self, direction):
        r = super(Randomhall, self).copy(Randomhall())
        r.rooms = self.rooms
        r.exit = self.exit
        r.probabilities = self.probabilities
        self.directions[direction] = r
        r.directions[globals()[direction.title()]().reverse] = self
        return r

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
                    grid[y][x] = self.copy()
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


    def copy(self):
        r = super(Grid, self).copy(Grid())
        r.exit = self.exit
        r.counts = self.counts
        return r

class Direction(object):
    name = ""

    @staticmethod
    def match(direction):
        for _direction in ["north", "south", "east", "west", "up", "down"]:
            if _direction.startswith(direction):
                return _direction
    
    @staticmethod
    def get_random(allowed_directions = []):
        return random.choice(allowed_directions if allowed_directions else \
            list(direction.name for direction in Direction.__subclasses__()))

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
    auto_room_name = 0

    def __init__(self):
        self.name = ""
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
            Area.auto_room_name = max(Area.auto_room_name, room.name)
            for mob in room.mobs():
                actor.actor.__proxy__.fire("actor_enters_realm", mob)
                room.arriving(mob)
                mob.start_room = room.name

    def __str__(self):
        return self.name
