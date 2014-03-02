from . import observer, mud, wireframes

class Actor(observer.Observer):
    
    def __init__(self):
        self.race = None
        self.room = None

        super(Actor, self).__init__()

    def set_race(self, race):
        if not isinstance(race, wireframes.race.Race):
            raise ValueError(str(race)+' must be of type Race')

        self.race = race