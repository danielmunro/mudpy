class Command(object):

    def __init__(self):
        self.name = ""
        self.required_dispositions = []
        self.messages = {}
    
    def __str__(self):
        return self.name
