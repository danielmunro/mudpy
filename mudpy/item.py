from save import Save

class Inventory:
	def __init__(self):
		self.id = Save.getRandomID()
		self.items = []
		self.itemCount = {}
	
	def append(self, item):
		self.items.append(item)
		k = str(item)
		if k in self.itemCount:
			self.itemCount[k] += 1
		else:
			self.itemCount[k] = 1
	
	def remove(self, item):
		try:
			self.items.remove(item)
			self.itemCount[str(item)] -= 1
		except ValueError:
			pass
	
	def inspection(self, appendToItemDisplayName = ""):
		msg = ""
		for i in iter(self.items):
			itemDisplayName = str(i)
			msg += ("("+str(self.itemCount[itemDisplayName])+") " if self.itemCount[itemDisplayName] > 1 else "")+itemDisplayName.capitalize()+appendToItemDisplayName+"\n"
		return msg
	
	def getWeight(self):
		return sum(item.weight for item in self.items)
	
	def save(self):
		Save(self, ['id', 'items']).execute()
	
	def load(self):
		from load import Load
		Load(self, ['id', 'items']).execute()

class Item(object):
	def __init__(self):
		self.id = Save.getRandomID()
		self.name = "a generic item"
		self.description = "a generic item is here"
		self.value = 0
		self.weight = 0
		self.material = ""
		self.canOwn = True
		self.level = 1
		self.repop = 1

	def __str__(self):
		return self.name
	
	def save(self):
		Save(self, ['id', 'name', 'value', 'weight']).execute()
	
	def load(self):
		from load import Load
		Load(self, ['id', 'name', 'value', 'weight']).execute()

class Door(Item):
	def __init__(self):
		self.disposition = ""
		self.directions = {}
		super(Door, self).__init__()
		self.canOwn = False

class Key(Item):
	def __init__(self):
		self.door_id = 0
		super(Key, self).__init__()

class Furniture(Item):
	def __init__(self):
		self.material = "generic"
		self.regen = 0
		super(Furniture, self).__init__()
		self.canOwn = False

class Container(Item):
	def __init__(self):
		self.inventory = Inventory()
		super(Container, self).__init__()

class Consumable(Item):
	def __init__(self):
		self.nourishment = 0
		super(Consumable, self).__init__()

class Food(Consumable):
	def __init__(self):
		self.nourishment = 0
		super(Food, self).__init__()

class Drink(Consumable):
	def __init__(self):
		self.refillable = True
		self.contents = ''
		self.uses = 1
		super(Drink, self).__init__()

class Equipment(Item):
	def __init__(self):
		self.position = ''
		self.condition = 1
		self.attributes = Attributes()
		super(Equipment, self).__init__()

class Armor(Equipment):
	def __init__(self):
		self.ac_slash = 0
		self.ac_bash = 0
		self.ac_pierce = 0
		self.ac_magic = 0
		super(Armor, self).__init__()

class Weapon(Equipment):
	def __init__(self):
		self.hit = 0
		self.dam = 0
		self.position = "held"
		self.verb = ""
		self.weaponType = ""
		self.damageType = ""
		super(Weapon, self).__init__()
