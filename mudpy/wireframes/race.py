from .. import wireframe

class Race(wireframe.Blueprint):
    """Gives various properties to an actor that have far reaching affects
    throughout the game.

    """

    yaml_tag = "u!race"

    SIZE_TINY = 1
    SIZE_SMALL = 2
    SIZE_NORMAL = 3
    SIZE_LARGE = 4
    SIZE_GIGANTIC = 5

    def __init__(self):
        self.name = "noop"
        self.size = self.SIZE_NORMAL
        self.movement_cost = 1
        self.is_playable = False
        self.dam_type = "bash"
        self.proficiencies = {}
        self.attributes = {}
        self.abilities = []
        self.affects = []
        self.experience = 1000;

    def __str__(self):
        return self.name