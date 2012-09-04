import sys, time, hashlib
from db import Db
from random import randint
from item import Inventory
from save import Save

class Room:
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
	
	def save(self):
		Save(self, ['id', 'title', 'description', 'directions']).execute()
	
	def __str__(self):
		return self.id

class RoomFactory:
	rooms = {}
	DEFAULT_ROOM = None

	def __init__(self):
		db = Db().getConnection()

		for i in db.smembers('rooms'):
			attrs = db.hgetall(i)
			r = Room()
			for k, n in attrs.iteritems():
				setattr(r, k, n)
			self.rooms[r.id] = r

		for i in self.rooms:
			if not self.DEFAULT_ROOM:
				self.DEFAULT_ROOM = self.rooms[i]
			attrs = db.hgetall(i+':directions')
			for k, n in attrs.iteritems():
				self.rooms[i].directions[k] = self.rooms[n]
