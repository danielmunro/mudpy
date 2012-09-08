import sys, time, hashlib
from random import randint
from attributes import Attributes
from item import Inventory
from save import Save

class Actor(object):
	def __init__(self):
		self.id = hashlib.sha224(str(time.time())+":"+str(randint(0, 1000000))).hexdigest()
		self.name = "an actor"
		self.long = "An actor is here"
		self.level = 0
		self.experience = 0
		self.attributes = self.getDefaultAttributes()
		self.max_attributes = self.getDefaultAttributes()
		self.sex = "neutral"
		self.room = None
		self.abilities = []
		self.target = None
		self.inventory = Inventory()
		self.race = ""
		"""
		self.equipped = {
			{'position':'light', 'equipped':None},
			{'position':'finger', 'equipped':None},
			{'position':'finger', 'equipped':None},
			{'position':'neck', 'equipped':None},
			{'position':'neck', 'equipped':None},
			{'position':'body', 'equipped':None},
			{'position':'head', 'equipped':None},
			{'position':'legs', 'equipped':None},
			{'position':'feet', 'equipped':None},
			{'position':'hands', 'equipped':None},
			{'position':'arms', 'equipped':None},
			{'position':'torso', 'equipped':None},
			{'position':'waist', 'equipped':None},
			{'position':'wrist', 'equipped':None},
			{'position':'wrist', 'equipped':None},
			{'position':'wield', 'equipped':None},
			{'position':'wield', 'equipped':None},
			{'position':'float', 'equipped':None}
		}
		"""
	
	def getMovementCost(self):
		# Add logic for carrying at maximum weight, injured, affects
		cost = 1
		if(self.isEncumbered()):
			cost += 1
		return cost
	
	def getMaxWeight(self):
		return 1+(self.level*100)
	
	def isEncumbered(self):
		return self.inventory.getWeight() > self.getMaxWeight() * 0.95
	
	def notify(self, message):
		return
	
	def tick(self):
		print "tick"

	def __str__(self):
		return self.name
	
	def getDefaultAttributes(self):
		a = Attributes()
		a.hp = 20
		a.mana = 20
		a.movement = 100
		a.ac_bash = 100
		a.ac_pierce = 100
		a.ac_slash = 100
		a.ac_magic = 100
		a.hit = 1
		a.dam = 1
		return a
	
	def save(self):
		Save(self, ['id', 'name', 'level', 'experience', 'attributes', 'max_attributes', 'sex', 'room', 'abilities', 'inventory']).execute()

class Mob(Actor):
	def __init__(self):
		self.movement = 1
		self.respawn = 1
		self.auto_flee = False
		self.area = None
		self.role = ''
		super(Mob, self).__init__()

class User(Actor):
	def prompt(self):
		return "%i %i %i >> " % (self.attributes.hp, self.attributes.mana, self.attributes.movement)
	
	def notify(self, message):
		self.client.write(message)
