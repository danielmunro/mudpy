"""Wireframes module."""

from . import debug, observer
import os, yaml, __main__

path = None
wireframes = {}

if '__mudpy__' in __main__.__dict__:

    m = __main__.__mudpy__

    def load_wireframes():
        global path

        path = m.path
        preload()

    def start_wireframes():
        load_areas()

    m.attach('initialize', load_wireframes)
    m.attach('start', start_wireframes)

def load_areas():
    from . import room, actor
    recurse(os.path.join(path, "areas"))

def preload(examine_path = "wireframes"):
    global wireframes
    start_path = os.path.join(path, examine_path)
    if os.path.isdir(start_path):
        for p in os.listdir(start_path):
            preload(os.path.join(examine_path, p))
    else:
        debug.log("preloading "+start_path)
        with open(start_path, "r") as fp:
            wireframes[start_path] = fp.read()

def recurse(path):
    """Load wireframes from initialization script, with slightly different 
    formatting than a persisted world.
    
    """

    if os.path.isdir(path):
        for infile in os.listdir(path):
            fullpath = path+'/'+infile
            recurse(fullpath)
    elif path.endswith('.yaml'):
        run(path)

def run(path):

    debug.log("running "+path)
    with open(path, "r") as fp:
        _object = yaml.load(fp)
        if 'done_init' in dir(_object) and callable(getattr(_object, 'done_init')):
            _object.done_init()

def create_from_match(search):
    parts = search.split('.')
    _file = parts[-1]
    _path = os.path.join(*[path, "wireframes"]+parts[0:-1])
    matches = {}
    try:
        for infile in os.listdir(_path):
            if infile.startswith(_file):
                i = os.path.join(_path, infile)
                if i in wireframes:
                    result = yaml.load(wireframes[i])
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

    wireframe_path = os.path.join(*[path]+subdirectory.split('.')+name.split('.'))+".yaml"
    if wireframe_path in wireframes:
        return yaml.load(wireframes[wireframe_path])
    try:
        with open(wireframe_path, "r") as fp:
            return yaml.load(fp)
    except IOError:
        pass
    raise WireframeException("wireframe does not exist: "+name)

def save(thing, subdirectory = "areas"):
    
    wireframe_path = os.path.join(*[path]+subdirectory.split('.')+[str(thing)])+".yaml"
    thing_yaml = yaml.dump(thing)
    with open(wireframe_path, "w") as fp:
        fp.write(thing_yaml)
    if subdirectory == "wireframes":
        wireframes[wireframe_path] = thing_yaml

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
