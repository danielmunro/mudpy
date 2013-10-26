from . import wireframe

class Game(wireframe.Blueprint):

    yaml_tag = "u!game"

    def __init__(self):
        self.observers = {}
        self.events = {}
