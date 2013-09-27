"""Wireframes module."""

from . import debug
import os, yaml

__wireframes__ = {}

def parse_dir(path):
    """Recursively scans a directory for mud configuration files to load."""

    if path.endswith('.yaml'):
        parse_yaml(path)
    elif os.path.isdir(path):
        for infile in os.listdir(path):
            fullpath = path+'/'+infile
            parse_dir(fullpath)

def parse_yaml(path):
    """Load a yaml config file and add the wireframes."""
    with open(path, "r") as fp:
        data = yaml.load(fp)
        for _class in data:
            for key in data[_class]:
                name = data[_class][key]['name']
                __wireframes__[name] = {
                    'class': _class,
                    'data': data[_class][key]
                }

def new(name):
    """Takes the given instance and assigns values to it from the internal 
    named lookup.

    Eg:

    ab = new(Ability(), "bash") # returns an Ability object with the assigned
                                # properties for bash
    
    """

    def do_import(name):
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

class Blueprint(object):
    """A basic object that is created using a wireframe. A dict of properties
    are passed to a blueprint, which are used to update the object's internal
    dict.

    """

    def __init__(self, **properties):
        self.__dict__.update(properties)
