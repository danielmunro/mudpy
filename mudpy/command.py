from . import debug

class Command(object):

    def __init__(self):
        self.name = ""
        self.required_dispositions = []

    def try_perform(self, performer, args = []):
        from . import actor
        if self.required_dispositions and performer.disposition \
                                not in self.required_dispositions:
            performer.notify("You are incapacitated and cannot do that." \
                if performer.disposition == actor.Disposition.INCAPACITATED \
                else "You need to be "+(" or ".join(self.required_dispositions))+" to do that.")
        else:
            try:
                getattr(performer, "command_"+self.name)(args)
            except AttributeError as e:
                debug.log(e, "notice")
    
    def __str__(self):
        return self.name
