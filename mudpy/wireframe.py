"""Wireframes module."""

from . import debug, observer
import os, yaml

__wireframes__ = {}

def repersist(path):
    """Load wireframes from previous game save."""

    global __wireframes__

    with open(path, "r") as fp:
        __wireframes__ = yaml.load(fp)

def load(path, recursed = False):
    """Load wireframes from initialization script, with slightly different 
    formatting than a persisted world.
    
    """

    if path.endswith('.yaml'):
        parse_yaml(path)
    elif os.path.isdir(path):
        for infile in os.listdir(path):
            fullpath = path+'/'+infile
            load(fullpath, True)
    elif not recursed:
        raise IOError(path+" not found")

def parse_yaml(path):
    """Load a yaml config file and add the wireframes."""

    debug.log("reading "+path)
    with open(path, "r") as fp:
        data = yaml.load(fp)
        for _class in data:
            for key in data[_class]:
                add(_class, key)

def add(_class, data):
    """Add a wireframe definition to the internal dict."""

    __wireframes__[data['name']] = {
        'class': _class,
        'data': data
    }

def save(data_dir):
    """Save all defined wireframes."""

    print "saving game state"

    path = os.path.join(data_dir, "wireframes.yaml")
    with open(path, "w") as fp:
        yaml.dump(__wireframes__, fp)


def new(name):
    """Creates an object from a name, a unique identifier for a wireframe.

    Eg:

    ab = new("gnome") # returns a new gnome race to assign to an actor
    
    """

    def do_import(name):
        """Dynamically import a class from a package name."""

        components = name.split('.')
        mod = __import__(".".join(components[:-1]), fromlist=[components[-1]])
        return getattr(mod, components[-1])

    try:
        found = __wireframes__[name]
    except KeyError:
        debug.log("wireframe does not exist for "+str(name), "error")
        raise

    __class__ = found['class']

    return do_import(__class__)(found['data'])

class Blueprint(observer.Observer):
    """A basic object that is created using a wireframe. A dict of properties
    are passed to a blueprint, which are used to update the object's internal
    dict.

    """

    def __init__(self, **properties):
        self.__dict__.update(properties)
        super(Blueprint, self).__init__()
        try:
            self.done_init()
        except AttributeError:
            pass

    def update(self):

        print "updating blueprint for "+str(self.name)

        global __wireframes__

        properties = self.__dict__.copy()
        try:
            properties.update(self.pre_update())
        except AttributeError:
            pass

        __wireframes__[self.name]['data'] = properties
