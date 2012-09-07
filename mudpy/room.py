import sys, time, hashlib
from random import randint
from item import Inventory

class Room:
	rooms = {}

	def __init__(self):
		self.id = hashlib.sha224(str(time.time())+":"+str(randint(0, 1000000))).hexdigest()
		self.title = ''
		self.description = ''
		self.directions = {'north': None, 'south': None, 'east': None, 'west': None, 'up': None, 'down': None}
		self.actors = []
		self.inventory = Inventory()

	def appendActor(self, actor):
		self.actors.append(actor)
	
	def removeActor(self, actor):
		self.actors.remove(actor)
	
	def notify(self, actor, message):
		for i, k in enumerate(self.actors):
			if k is actor:
				continue
			else:
				k.notify(message)
	
	def getActorByName(self, name):
		for i in iter(self.actors):
			if i.name.lower().find(name.lower()) > -1:
				return i
	
	def __str__(self):
		return self.id

class Area:
	def __init__(self):
		self.name = ""
		self.terrain = ""
		self.location = ""
