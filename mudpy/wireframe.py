"""Wireframes module."""

from . import debug, observer
import os, yaml

__wireframes__ = {}

def load(path, recursed = False):
    """Recursively scans a directory for mud configuration files to load."""

    global __wireframes__

    if not recursed and path.endswith('.yaml'):
        with open(path, "r") as fp:
            __wireframes__ = yaml.load(fp)
        return

    if path.endswith('.yaml'):
        parse_yaml(path)
    elif os.path.isdir(path):
        for infile in os.listdir(path):
            fullpath = path+'/'+infile
            load(fullpath, True)

def parse_yaml(path):
    """Load a yaml config file and add the wireframes."""

    debug.log("reading "+path)
    with open(path, "r") as fp:
        data = yaml.load(fp)
        for _class in data:
            for key in data[_class]:
                name = key['name']
                del key['name']
                add(name, _class, key)

def add(name, _class, data):
    __wireframes__[name] = {
        'class': _class,
        'data': data
    }

def save(data_dir):
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
        debug.log("wireframe does not exist for "+name, "error")
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
