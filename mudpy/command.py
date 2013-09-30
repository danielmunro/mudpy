from . import wireframe

class Command(wireframe.Blueprint):

    def __init__(self, properties):
        self.name = ""
        self.required_dispositions = []
        self.messages = {}
        super(Command, self).__init__(**properties)
    
    def __str__(self):
        return self.name
