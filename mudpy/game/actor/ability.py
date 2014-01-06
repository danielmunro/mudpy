from ...sys import wireframe
import random

class Ability(wireframe.Blueprint):
    """Represents something cool an actor can do. Invoked when the hook is
    triggered on the parent actor. Applies costs in the costs dict, and affects
    in the affects list.
    
    """

    yaml_tag = "u!ability"

    def __init__(self):
        self.level = 0
        self.affects = []
        self.costs = {}
        self.delay = 0
        self.type = "" # skill or spell
        self.hook = ""
        self.aggro = False
        self.messages = {}
    
    def try_perform(self, invoker, args):
        """Parses the user input, finds a target, applies the ability cost,
        and invokes the ability.

        """

        receiver = None
        try:
            args = args[0]
            receiver = invoker.get_room().get_actor(args[-1])
        except IndexError:
            pass
        if not receiver:
            receiver = invoker
        if self.apply_cost(invoker):
            invoker.delay_counter += self.delay + 1
            success = random.randint(0, 1)
            if success:
                self.perform(receiver)
            else:
                invoker.notify('failed')
        else:
            invoker.notify(__config__['messages']['apply_cost_fail'])

    def perform(self, receiver):
        """Initialize all the affects associated with this ability."""

        from .. import affect

        for affectname in self.affects:
            receiver.add_affect(wireframe.create(affectname))
    
    def apply_cost(self, invoker):
        """Iterates over the cost property, checks that all requirements are
        met, applies each cost, then returns true. If costs cannot be met by
        the invoking actor, this method will return false.

        """

        for attr, cost in self.costs.items():
            curattr = getattr(invoker, 'cur'+attr)
            cost *= curattr if cost > 0 and cost < 1 else 1
            if curattr < cost:
                return False
        for attr, cost in self.costs.items():
            curattr = getattr(invoker, 'cur'+attr)
            cost *= curattr if cost > 0 and cost < 1 else 1
            setattr(invoker, 'cur'+attr, curattr-cost)
        return True
    
    def __str__(self):
        return self.name
