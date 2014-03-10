from .. import wireframe

class Ability(wireframe.Blueprint):
    """Represents something cool an actor can do. Invoked when the hook is
    triggered on the parent actor. Applies costs in the costs dict, and affects
    in the affects list.
    
    """

    yaml_tag = "u!ability"

    def __init__(self, _publisher):
        self.level = 0
        self.affects = []
        self.costs = {}
        self.delay = 0
        self.type = "" # skill or spell
        self.hook = ""
        self.aggro = False
        self.messages = {}
    
    def __str__(self):
        return self.name