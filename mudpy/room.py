from item import Inventory
from random import random, choice

__START_ROOM__ = None
__ROOMS__ = {}

class Room(object):

    def __init__(self):
        self.id = 0
        self.name = ''
        self.description = ''
        self.actors = []
        self.inventory = Inventory()
        self.directions = {}
        self.area = None
    
    def notify(self, notifier, message):
        for actor in list(actor for actor in self.actors if not actor is notifier):
            actor.notify(message+"\n")
    
    def announce(self, messages):
        announcedActors = []
        generalMessage = ""
        for actor, message in messages.iteritems():
            if actor == "*":
                generalMessage = message
            else:
                if message:
                    actor.notify(message+"\n")
                announcedActors.append(actor)
        if generalMessage:
            for actor in list(set(self.actors) - set(announcedActors)):
                actor.notify(generalMessage+"\n")
    
    def mobs(self):
        from actor import Mob
        return list(actor for actor in self.actors if isinstance(actor, Mob))

    def copy(self, newRoom):
        newRoom.name = self.name
        newRoom.description = self.description
        newRoom.area = self.area
        newRoom.initialize_directions()
        return newRoom

    def get_full_id(self):
        return self.area.name+":"+str(self.id)
    
    def initialize_directions(self):
        for direction in Direction.__subclasses__():
            try:
                self.directions[direction.name]
            except KeyError:
                self.directions[direction.name] = None
    
    def __str__(self):
        return self.name

class Randomhall(Room):
    def __init__(self):
        super(Randomhall, self).__init__()
        self.rooms = 0
        self.exit = 0
        self.probabilities = dict((direction, .5) for direction in self.directions)
    
    def buildDungeon(self, roomCount = 0):
        direction = Direction.get_random(list(direction for direction, room in self.directions.iteritems() if not room))
        if self.probabilities[direction] > random():
            if self.rooms < roomCount:
                exit = __ROOMS__[self.area.name+":"+str(self.exit)]
                self.directions[direction] = exit
                exit.directions[globals()[direction.title()]().reverse] = self
            else:
                return self.copy(direction).buildDungeon(roomCount+1)
        else:
            rooms = list(room for room in self.directions.values() if isinstance(room, Randomhall))
            if rooms:
                return choice(rooms).buildDungeon(roomCount)
        return roomCount;
    
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
            rand_x = int(round(random()*xlen))
            rand_y = int(round(random()*ylen))
            direction = Direction.get_random()
            if not grid[rand_y][rand_x].directions[direction]:
                room_key = self.area.name+":"+str(exit)
                grid[rand_y][rand_x].directions[direction] = __ROOMS__[room_key]
                __ROOMS__[room_key].directions[globals()[direction.title()].reverse] = grid[rand_y][rand_x]
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
        return choice(allowedDirections if allowedDirections else list(direction.name for direction in Direction.__subclasses__()))

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

class Area:
    def __init__(self):
        self.name = ""
        self.terrain = ""
        self.location = ""

class Reporter:

    def getMessages(self, messagePart, invoker, receiver = None):
        messages = self.messages[messagePart]
        try:
            messages[invoker] = messages.pop('invoker')
            if messages[invoker].find('%s') > -1:
                messages[invoker] = messages[invoker] % str(receiver)
        except KeyError: pass
        try:
            messages[receiver] = messages.pop('receiver')
            if messages[receiver].find('%s') > -1:
                messages[receiver] = messages[receiver] % str(receiver)
        except KeyError: pass
        try:
            messages['*'] = messages.pop('*')
            if messages['*'].find('%s') > -1:
                messages['*'] = messages['*'] % str(invoker)
            if messages['*'].find('%s') > -1:
                messages['*'] = messages['*'] % str(receiver)
        except KeyError: pass
        return messages
