from . import wireframe

class Command(wireframe.Blueprint):

    yaml_tag = "u!command"

    def __init__(self):
        self.name = ""
        self.required_dispositions = []
        self.messages = {}
    
    def __str__(self):
        return self.name
