"""Rooms in a mud represent the physical space in which the creatures, mobs,
items, and players occupy. They can be towns, trails, forests, mines, oceans,
dungeons, and more.

"""

from . import item, observer, wireframe
import random

__START_ROOM__ = None
__PURGATORY__ = None
__ROOMS__ = {}
__AREAS__ = {}

__LAST_AREA__ = None
__LOCATION_OUTSIDE__ = "outside"

def get(room_name):
    return __ROOMS__[room_name]

def area(area_name):
    return __AREAS__[area_name]

class Room(wireframe.Blueprint):
    """Basic space representation game configuration files. Has a name (title),
    description, a list of actors in the room, an inventory of items, and a
    dictionary of possible directions to leave.

    """

    yaml_tag = "u!room"

    def __init__(self):
        self.name = ''
        self.title = ''
        self.description = ''
        self.actors = []
        self.inventory = []
        self.directions = {}
        self.area = ''
        self.lit = True
        self.observers = {}

    def get_area(self):
        return area(self.area)
    
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
        from actor import Mob
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
        self.actors.remove(actor)
        self.detach('actor_changed', actor.room_update)

    def arriving(self, actor, direction = ""):
        self.actors.append(actor)
        actor.room = self.name
        self.attach('actor_changed', actor.room_update)
    
    @classmethod
    def to_yaml(self, dumper, thing):
        from . import actor
        import copy
        persist = copy.copy(thing)
        persist.actors = [i for i in persist.actors if isinstance(i, actor.Mob)]
        return super(Room, self).to_yaml(dumper, persist)

    def __str__(self):
        return self.name

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
                exit = __ROOMS__[self.area.name+":"+str(self.exit)]
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
                grid[rand_y][rand_x].directions[direction] = __ROOMS__[room_key]
                class_name = direction.title()
                __ROOMS__[room_key].directions[globals()[class_name].reverse]=\
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
    def get_random(allowedDirections = []):
        return random.choice(allowedDirections if allowedDirections else \
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

    def __init__(self):
        self.name = ""
        self.terrain = ""
        self.location = ""
        self.rooms = []

    def done_init(self):
        __AREAS__[self.name] = self
        for room in self.rooms:
            __ROOMS__[room.name] = room
            room.area = self.name
            for m in room.mobs():
                m.room = room.name

    def __str__(self):
        return self.name
