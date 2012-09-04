import sys, time, hashlib
from random import randint
from save import Save

class Attributes:
	def __init__(self):
		self.id = hashlib.sha224(str(time.time())+":"+str(randint(0, 1000000))).hexdigest()
		self.hp = 0
		self.mana = 0
		self.movement = 0

		self.bless = 0

		self.ac_bash = 0
		self.ac_pierce = 0
		self.ac_slash = 0
		self.ac_magic = 0

		self.hit = 0
		self.dam = 0
	
	def save(self):
		Save(self, ['id', 'hp', 'mana', 'movement', 'bless', 'ac_bash', 'ac_pierce', 'ac_slash', 'ac_magic', 'hit', 'dam']).execute()
