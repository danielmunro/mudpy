class Inventory:
	def __init__(self):
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

class Item(object):
	name = 'a generic item'
	value = 0

	def __str__(self):
		return self.name

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
