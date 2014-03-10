from . import observer, mud
import yaml

class Blueprint(observer.Observer, yaml.YAMLObject):

    def __init__(self):
        self.id = 0
        self.name = "noop"
        self.short_desc = "A noop is here."
        self.long_desc = "A noop is here, from the land of Noops. It seems out of place."
        
        super(Blueprint, self).__init__()

    @classmethod
    def from_yaml(cls, loader, node):
        data = loader.construct_mapping(node)
        self = cls(mud.__instance__)
        self.__dict__.update(data)
        self.observers = {}
        return self

    @classmethod
    def to_yaml(self, dumper, thing):
        data = thing.__dict__.copy()
        if 'observers' in data:
            del data['observers']
        return dumper.represent_mapping(thing.yaml_tag, data)