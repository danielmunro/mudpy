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

def create_from_match(search):
    parts = search.split('.')
    _file = parts[-1]
    _path = os.path.join(*[path, "wireframes"]+parts[0:-1])
    try:
        for infile in os.listdir(_path):
            if infile.startswith(_file):
                with open(os.path.join(_path, infile), "r") as fp:
                    return yaml.load(fp)
    except OSError:
        pass
    raise WireframeException("wireframe match not found: "+search)

def create(name, subdirectory = "wireframes"):
    """Creates an object from a name, a unique identifier for a wireframe.

    Eg:

    race = create("gnome") # returns a new gnome race to assign to an actor
    
    """

    wireframe_path = os.path.join(*[path]+subdirectory.split('.')+name.split('.'))+".yaml"

    try:
        with open(wireframe_path, "r") as fp:
            return yaml.load(fp)
    except IOError:
        raise WireframeException("wireframe does not exist: "+name)

def save(thing, subdirectory = "areas"):
    
    wireframe_path = os.path.join(*[path, subdirectory, str(thing)])+".yaml"
    with open(wireframe_path, "w") as fp:
        yaml.dump(thing, fp)

class Blueprint(observer.Observer, yaml.YAMLObject):

    @classmethod
    def from_yaml(cls, loader, node):
        data = loader.construct_mapping(node)
        if "wireframe" in data:
            self = create(data['wireframe'])
        else:
            self = cls()
            self.__dict__.update(data)
        self.observers = {}
        return self

    @classmethod
    def to_yaml(self, dumper, thing):
        data = thing.__dict__
        if 'observers' in data:
            del data['observers']
        node = dumper.represent_mapping(thing.yaml_tag, data)
        return node

class WireframeException(Exception):
    pass
