"""Wireframes module."""

from . import debug, observer
import os, yaml, sys

__path__ = None
wireframes = {}

def preload(examine_path = "wireframes"):
    """Setup wireframes data."""

    start_path = os.path.join(__path__, examine_path)
    if os.path.isdir(start_path):
        for p in os.listdir(start_path):
            preload(os.path.join(examine_path, p))
    else:
        debug.log("preloading "+start_path)
        global wireframes
        with open(start_path, "r") as fp:
            wireframes[start_path] = fp.read()

if len(sys.argv) > 1:
    __path__ = sys.argv[1]
    preload()
else:
    debug.error("Needs path, ie python main.py example")
    sys.exit()

def load_areas():
    """Load areas defined in the path."""

    from ..game import room
    from ..game.actor import mob, race
    _load_areas(os.path.join(__path__, "areas"))

def _load_areas(path):
    """Load wireframes from initialization script, with slightly different 
    formatting than a persisted world.
    
    """

    if os.path.isdir(path):
        for infile in os.listdir(path):
            fullpath = path+'/'+infile
            _load_areas(fullpath)
    elif path.endswith('.yaml'):
        run(path)

def run(path):
    """Load a yaml file and optionally call a done callback."""

    debug.log("running "+path)
    with open(path, "r") as fp:
        _object = load_yaml(fp)
        if 'done_init' in dir(_object) and callable(getattr(_object, 'done_init')):
            _object.done_init()

def create_from_match(search):
    """Parse a yaml object from a partial match."""

    parts = search.split('.')
    _file = parts[-1]
    _path = os.path.join(*[__path__, "wireframes"]+parts[0:-1])
    matches = {}
    try:
        for infile in os.listdir(_path):
            if infile.startswith(_file):
                i = os.path.join(_path, infile)
                if i in wireframes:
                    result = load_yaml(wireframes[i])
                    priority = result.priority if 'priority' in result.__dict__ else 0
                    matches[priority] = result
    except OSError:
        pass
    if matches:
        return matches[max(matches.keys())]
    raise WireframeException("wireframe match not found: "+search)

def create(name, subdirectory = "wireframes"):
    """Creates an object from a name, a unique identifier for a wireframe.

    Eg:

    race = create("gnome") # returns a new gnome race to assign to an actor
    
    """

    wireframe_path = os.path.join(*[__path__]+subdirectory.split('.')+name.split('.'))+".yaml"
    if wireframe_path in wireframes:
        return load_yaml(wireframes[wireframe_path])
    try:
        with open(wireframe_path, "r") as fp:
            return load_yaml(fp)
    except IOError:
        raise WireframeException

def save(thing, subdirectory = "areas"):
    """Persist an object."""
    
    wireframe_path = os.path.join(*[__path__]+subdirectory.split('.')+[str(thing)])+".yaml"
    thing_yaml = yaml.dump(thing)
    with open(wireframe_path, "w") as fp:
        fp.write(thing_yaml)
    if subdirectory == "wireframes":
        wireframes[wireframe_path] = thing_yaml

def load_yaml(fp):
    """Wrapper to load YAML data."""

    return yaml.load(fp)

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
        if "wireframe" in data:
            self = create(data['wireframe'])
        else:
            self = cls()
            self.__dict__.update(data)
        self.observers = {}
        return self

    @classmethod
    def to_yaml(self, dumper, thing):
        data = thing.__dict__.copy()
        if 'observers' in data:
            del data['observers']
        node = dumper.represent_mapping(thing.yaml_tag, data)
        return node

class WireframeException(Exception):
    pass
