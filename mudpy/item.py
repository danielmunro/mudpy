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

	def __str__(self):
		return self.name
	
	def save(self):
		Save(self, ['id', 'name', 'value', 'weight'])

class Consumable(Item):
	nourishment = 0

class Food(Consumable):
	nourishment = 0

class Drink(Consumable):
	refillable = True
	drink = ''
	amount = 1

class Equipment(Item):
	position = ''
	condition = 1

class Armor(Equipment):
	ac_slash = 0
	ac_bash = 0
	ac_pierce = 0
	ac_magic = 0

class Weapon(Equipment):
	hit = 0
	dam = 0
	position = 'held'
