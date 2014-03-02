from .. import wireframe

class Room(wireframe.Blueprint):

    def __init__(self):

        self.short_desc = "A nondescript room"
        self.long_desc = "You find yourself in a fairly uninteresting room."

        self.directions = dict((d.name, None) for d in Direction.get_all())

        super(Room, self).__init__()


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