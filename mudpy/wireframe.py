"""Wireframes module."""

from . import debug, observer
import os, yaml

path = None

def execute():
    recurse(os.path.join(path, "areas"))

def recurse(path, onceLoaded = False):
    """Load wireframes from initialization script, with slightly different 
    formatting than a persisted world.
    
    """

    if path.endswith('.yaml'):
        run(path)
        onceLoaded = True
        return
    elif os.path.isdir(path):
        for infile in os.listdir(path):
            fullpath = path+'/'+infile
            recurse(fullpath, onceLoaded)
        return
    
    if not onceLoaded:
        raise IOError(path+" not found or not valid")

def run(path):

    debug.log("running: "+path)
    with open(path, "r") as fp:
        _object = yaml.load(fp)
        try:
            _object.done_init()
        except AttributeError:
            pass

def create(name):
    """Creates an object from a name, a unique identifier for a wireframe.

    Eg:

    race = create("gnome") # returns a new gnome race to assign to an actor
    
    """

    wireframe_path = os.path.join(*[path, "wireframes"]+name.split('.'))+".yaml"

    try:
        with open(wireframe_path, "r") as fp:
            return yaml.load(fp)
    except IOError:
        raise WireframeException("wireframe does not exist: "+name)

class Blueprint(observer.Observer, yaml.YAMLObject):

    @classmethod
    def from_yaml(cls, loader, node):
        data = loader.construct_mapping(node)
        if "wireframe" in data:
            self = create(data['wireframe'])
        else:
            self = cls()
            self.__dict__.update(data)
        try:
            self.done_init()
        except AttributeError:
            pass
        return self

    """
    @classmethod
    def to_yaml(self, dumper, data):
        del data['observers']
        node = dumper.represent_mapping(data)
        return node
        """

class WireframeException(Exception):
    pass
