"""All physical objects in the game besides actors are represented by the
classes in this module, and are generally things that actors can manipulate in
different ways.

"""

class Inventory:
    """A bucket of items."""

    def __init__(self):
        self.items = []
        self.item_count = {}
    
    def append(self, item):
        """Add a new item to the bucket and keep track of how many items the
        inventory has by that name.

        """

        self.items.append(item)
        k = str(item)
        if k in self.item_count:
            self.item_count[k] += 1
        else:
            self.item_count[k] = 1
    
    def remove(self, item):
        """Remove an item from the bucket."""

        try:
            self.items.remove(item)
            self.item_count[str(item)] -= 1
        except ValueError:
            pass
    
    def inspection(self, append_to_name = ""):
        """Slightly modified __str__ -type method, with the ability to append a
        string to each item.

        """

        msg = ""
        for i in iter(self.items):
            item_name = str(i)
            msg += ("("+str(self.item_count[item_name])+") " if \
                    self.item_count[item_name] > 1 else "")+ \
                    item_name[0].upper()+item_name[1:]+ \
                    append_to_name+"\n"
        return msg
    
    def get_weight(self):
        """Return the sum total weight of the items in the inventory."""

        return sum(item.weight for item in self.items)
    
    def __str__(self):
        return self.inspection()

class Item(object):
    """Generic item class for properties shared across all item types."""

    def __init__(self):
        self.name = "a generic item"
        self.description = "a generic item is here"
        self.value = 0
        self.weight = 0
        self.material = ""
        self.can_own = True
        self.level = 1
        self.repop = 1

    def __str__(self):
        return self.name

class Door(Item):
    """Doors go in between rooms, and can be open, closed, or locked."""

    def __init__(self):
        self.disposition = ""
        self.directions = {}
        super(Door, self).__init__()
        self.can_own = False

class Key(Item):
    """Keys can unlock or lock matching doors."""

    def __init__(self):
        self.door_id = 0
        super(Key, self).__init__()

class Furniture(Item):
    """Alters regen for actors that rest on this item."""

    def __init__(self):
        self.material = "generic"
        self.regen = 0
        super(Furniture, self).__init__()
        self.can_own = False

class Container(Item):
    """An item that has an inventory."""

    def __init__(self):
        self.inventory = Inventory()
        super(Container, self).__init__()

class Consumable(Item):
    """An item that can be eaten or drank by an actor."""

    def __init__(self):
        self.nourishment = 0
        super(Consumable, self).__init__()

class Food(Consumable):
    """Edible items."""

    def __init__(self):
        self.nourishment = 0
        super(Food, self).__init__()

class Drink(Consumable):
    """Drinkable items."""

    def __init__(self):
        self.refillable = True
        self.contents = ''
        self.uses = 1
        super(Drink, self).__init__()

class Equipment(Item):
    """Items that can be worn as weapons or armor."""

    def __init__(self):
        self.position = ''
        self.condition = 1
        self.attributes = {}
        super(Equipment, self).__init__()

    def get_attribute(self, attr):
        try:
            return self.attributes[attr]
        except KeyError:
            return 0

class Armor(Equipment):
    """Items that can be equipped as armor."""

    def __init__(self):
        self.ac_slash = 0
        self.ac_bash = 0
        self.ac_pierce = 0
        self.ac_magic = 0
        super(Armor, self).__init__()

class Weapon(Equipment):
    """Items that can be equipped as weapons."""

    def __init__(self):
        self.hit = 0
        self.dam = 0
        self.position = "held"
        self.verb = ""
        self.weapon_type = ""
        self.damage_type = ""
        super(Weapon, self).__init__()

class Corpse(Container):
    """Item that generates when an actor dies."""

    pass
