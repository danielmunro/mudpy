"""Parses data about game objects, loads wireframes, and creates objects
based on wireframes.

"""

from . import debug, room
import os, json, operator

__wireframes__ = {}
__loaded__ = []
__deferred__ = []
__lastarea__ = None
__INITFILE__ = 'init.json'

def new(instance, name):
    """Takes the given instance and assigns values to it from the internal 
    named lookup.

    Eg:

    ab = new(Ability(), "bash") # returns an Ability object with the assigned
                                # properties for bash
    
    """

    key = instance.__module__+'.'+instance.__class__.__name__

    try:
        found = __wireframes__[key][name]
    except KeyError:
        raise FactoryException("Factory does not know how to create "+str(name))
    return build(instance, found[key])

def add(wireframes):
    """Adds a new wireframe definition for an instance type."""

    for wireframe in wireframes:
        for key, blob in wireframe.iteritems():
            name = blob['properties']['name']
            debug.log('factory adding wireframe design for '+name)
            try:
                __wireframes__[key][name] = wireframe
            except KeyError:
                __wireframes__[key] = {}
                __wireframes__[key][name] = wireframe

def match(name, keys, scalar = True):
    """Performs a fuzzy lookup for wireframes by name."""

    matches = []
    if not isinstance(keys, list):
        keys = [keys]
    for key in keys:
        for wireframename, wireframe in __wireframes__[key].iteritems():
            if wireframename.startswith(name):
                record = {'key':key, 'wireframe':wireframename}
                try:
                    record['priority'] = wireframe[key]['priority']
                except KeyError:
                    record['priority'] = 0
                matches.append(record)
    matches = sorted(matches, key=operator.itemgetter('priority'))
    matches.reverse()
    try:
        return matches[0] if scalar else matches
    except IndexError:
        return None

def parse(path):
    """Parses a base scripts path in order to load the initial game objects
    and wireframes, which will be used later by the factory to build game
    objects.

    """

    global __deferred__

    if not os.path.isdir(path):
        raise IOError(path+" not a valid scripts directory")

    _parse(path)
    while len(__deferred__):
        startlen = len(__loaded__)
        deferred = __deferred__
        __deferred__ = []
        for fullpath in deferred:
            _parse(fullpath)
        endlen = len(__loaded__)
        if startlen == endlen:
            debug.log("dependencies cannot be met", "error")

    #build out the room tree
    random_halls = []
    grids = []
    for room_id, _room in room.__ROOMS__.iteritems():
        _room.initialize_directions()
        if isinstance(_room, room.Randomhall):
            random_halls.append(_room)
        if isinstance(_room, room.Grid):
            grids.append(_room)
        for direction_id, direction in room.__ROOMS__[room_id].directions.items():
            if direction:
                try:
                    if type(direction) is int:
                        direction = room.__ROOMS__[room_id].area.name+":"+str(direction)
                    room.__ROOMS__[room_id].directions[direction_id] = room.__ROOMS__[direction]
                except KeyError:
                    debug.log("Room id "+str(direction)+" is not defined, removing", "notice")
                    del room.__ROOMS__[room_id].directions[direction_id]
    for _room in random_halls:
        room_count = _room.buildDungeon()
        while room_count < _room.rooms:
            room_count = _room.buildDungeon(room_count)
    for _room in grids:
        rows = _room.counts['west'] + _room.counts['east']
        rows = rows if rows > 0 else 1
        cols = _room.counts['north'] + _room.counts['south']
        cols = cols if cols > 0 else 1
        grid = [[row for row in range(rows)] for col in range(cols)]
        grid[_room.counts['north']-1][_room.counts['west']-1] = _room
        _room.buildDungeon(0, 0, grid)

    debug.log('scripts initialized')

def _parse(path):
    """Called by parse(), recursively explores a directory tree and attempts
    to load json data.

    """

    debug.log('recurse through path: '+path)

    if path.endswith('.json'):
        return parse_json(path) # parse the json file

    # check that dependencies for the directory have been met
    init = path+'/'+__INITFILE__
    if os.path.isfile(init) and not parse_json(init):
        return

    if os.path.isdir(path):
        # parse through this directory
        for infile in os.listdir(path):
            fullpath = path+'/'+infile
            if fullpath == init:
                continue # skip the init file
            _parse(fullpath)

def parse_json(script):
    """Parses a json data file and loads game objects and/or wireframes."""

    debug.log('parsing json file: '+script)
    fp = open(script)
    try:
        data = json.load(fp)
    except ValueError:
        debug.log("script file is not properly formatted: "+script, "error")
    path, filename = os.path.split(script)
    try:
        _parse_json(data)
        __loaded__.append(filename)
        return True
    except DependencyException:
        debug.log(script+' deferred')
        __deferred__.append(path if filename == __INITFILE__ else script)
        return False

def _parse_json(data, parent = None):
    """Called by parse_json(), loops through array of json data and builds a
    list of game objects from the data.

    """

    for item in data:
        for _class in item:
            _class = str(_class)
            if "." in _class:
                module_parts = _class.split(".")
                module = __import__(module_parts[0]+"."+module_parts[1], fromlist=[module_parts[1]])
                instance = getattr(module, module_parts[2])()
                build(instance, item[_class], parent)
            else:
                build(None, item, parent)

def build(instance, properties, parent = None):
    """Takes an instance of a game object and a list of properties and call
    desc_* methods to build the properties of the game object.

    """

    for descriptor in properties:
        func = 'desc_'+descriptor
        value = properties[descriptor]
        if isinstance(value, unicode):
            value = str(value)
        try:
            globals()[func](instance, properties[descriptor])
        except KeyError:
            pass
    func = 'done_'+instance.__class__.__name__.lower()
    try:
        globals()[func](parent, instance)
    except KeyError:
        pass
    return instance

def desc_wireframes(none, wires):
    """Wireframe descriptor method, for adding wireframe definitions to the
    factory for later object initialization.

    """

    add(wires)

def desc_abilities(instance, abilities):
    """Abilities descriptor method, assigns abilities to a game object."""

    from . import actor

    for ability in abilities:
        instance.abilities.append(new(actor.Ability(), ability))

def desc_affects(instance, affects):
    """Affects descriptor method, assigns affects to a game objects."""

    from . import affect
    for aff in affects:
        instance.affects.append(new(affect.Affect(), aff))

def desc_proficiencies(actor, proficiencies):
    """Proficiencies descriptor method, assigns proficiencies to a game object."""

    for proficiency in proficiencies:
        actor.addProficiency(proficiency, proficiencies[proficiency])

def desc_inventory(instance, inventory):
    """Inventory descriptor method, calls _parse_json() to initialize the items
    for the inventory.
    
    """

    _parse_json(inventory, instance)

def desc_mobs(instance, mobs):
    """Mob descriptor method, calls _parse_json() to initialize all of the
    mob's properties.

    """

    _parse_json(mobs, instance)

def desc_properties(instance, properties):
    """Properties descriptor method, assigns class properties directly to the
    game object instance.
    
    """

    for prop in properties:
        setattr(instance, prop, properties[prop])

def desc_attributes(instance, attributes):
    """Attributes descriptor method, sets properties for the game object
    instance's attributes, such as hp, mana, movement, str, int, etc.

    """

    for attribute in attributes:
        setattr(instance.attributes, attribute, attributes[attribute])

def done_depends(parent, depends):
    """Raises a DependencyException when the parser begins to parse a script
    whose dependencies have not yet been met.

    """

    deps = [dep for dep in depends.on if not dep in __loaded__]
    if len(deps):
        raise DependencyException

def done_area(parent, area):
    """Sets the lastarea variable which is then used to set room.area for
    each new room.

    """

    global __lastarea__

    __lastarea__ = area

def done_mob(parent, mob):
    """Finish initializing a mob."""

    from . import actor, server
    parent.actor_arrive(mob)
    mob.room = parent
    mob.race = new(actor.Race(), mob.race)
    server.__instance__.heartbeat.attach('tick', mob.tick)

def done_room(parent, _room):
    """Last steps to finalize parsing a room."""

    _room.area = __lastarea__

    try:
        room.__ROOMS__[_room.get_full_id()] = _room
    except AttributeError:
        pass

    try:
        room.__START_ROOM__ = _room.__START_ROOM__
    except AttributeError:
        pass

def done_grid(parent, room):
    done_room(parent, room)

def done_randomhall(parent, room):
    done_room(parent_room)

def done_item(parent, item):
    """Attach an item to the parent's inventory."""

    parent.inventory.append(item)

def done_drink(parent, drink):
    """Attach the drink to the parent's inventory."""

    parent.inventory.append(drink)
    
class Depends:
    """Creates a Depends object for tracking script dependencies."""

    def __init__(self):
        self.on = []

class DependencyException(Exception):
    """Thrown when a parser is attempting to read a script that has unmet
    dependencies.

    """

    pass

class FactoryException(Exception):
    """Thrown when a factory does not know how to create the object that is
    requested.

    """

    pass
