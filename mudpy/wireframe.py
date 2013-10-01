"""Wireframes module."""

from . import debug
import os, yaml

__wireframes__ = {}

def execute(path):
    recurse(run, path)

def load(path):
    recurse(add_wireframe_file, path)

def recurse(method, path, onceLoaded = False):
    """Load wireframes from initialization script, with slightly different 
    formatting than a persisted world.
    
    """

    if path.endswith('.yaml'):
        method(path)
        onceLoaded = True
        return
    elif os.path.isdir(path):
        for infile in os.listdir(path):
            fullpath = path+'/'+infile
            recurse(method, fullpath, onceLoaded)
        return
    
    if not onceLoaded:
        raise IOError(path+" not found or not valid")

def add_wireframe_file(path):
    """Load a yaml config file and add the wireframes."""

    debug.log("adding to wireframe: "+path)
    with open(path, "r") as fp:
        __wireframes__.update(yaml.load(fp))

def run(path):

    debug.log("running: "+path)
    with open(path, "r") as fp:
        _object = yaml.load(fp)
        try:
            _object.done_init()
        except AttributeError:
            pass

def add(name, data):
    """Add a wireframe definition to the internal dict."""

    __wireframes__[name] = data

def save(data_dir):
    """Save all defined wireframes."""

    print "saving game state"

    path = os.path.join(data_dir, "wireframes.yaml")
    with open(path, "w") as fp:
        yaml.dump(__wireframes__, fp)


def apply(_object, name):
    """Creates an object from a name, a unique identifier for a wireframe.

    Eg:

    ab = new("gnome") # returns a new gnome race to assign to an actor
    
    """

    try:
        _object.__dict__.update(__wireframes__[name])
    except KeyError:
        debug.log("wireframe not found: "+name, "error")
        raise

    return _object
