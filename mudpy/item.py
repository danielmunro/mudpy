import sys, time, hashlib
from random import randint
from save import Save

class Inventory:
	def __init__(self):
		self.id = hashlib.sha224(str(time.time())+":"+str(randint(0, 1000000))).hexdigest()
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
	
	def getByName(self, name):
		for i in iter(self.items):
			if i.name.find(name):
				return i

	def inspection(self):
		msg = ""
		for i, n in self.itemCount.iteritems():
			msg += ("("+str(n)+") " if n > 1 else "")+i+"\n"
		return msg
	
	def getWeight(self):
		weight = 0
		for i in self.items:
			weight += i.weight
		return weight
	
	def save(self):
		Save(self, ['id', 'items']).execute()

class Item(object):
	def __init__(self):
		self.id = hashlib.sha224(str(time.time())+":"+str(randint(0, 1000000))).hexdigest()
		self.name = 'a generic item'
		self.value = 0
		self.weight = 0
		self.material = ""
		self.can_own = True
		self.level = 1

	def __str__(self):
		return self.name
	
	def save(self):
		Save(self, ['id', 'name', 'value', 'weight'])

class Door(Item):
	def __init__(self):
		self.disposition = ""
		super(Door, self).__init__()
		self.can_own = False

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
		self.position = 'held'
		super(Weapon, self).__init__()
