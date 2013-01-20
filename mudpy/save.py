import time, hashlib
from random import randint
from db import Db

class Save:
	def __init__(self, saved, properties):
		self.saved = saved
		self.properties = properties
		self.entity = saved.__class__.__name__
	
	def execute(self):
		# get connection
		db = Db().conn

		# ensure the object has an id
		if not self.saved.id:
			self.saved.id = self.getRandomID()

		# save the object's id in the entity set
		db.sadd(self.entity, self.saved.id)

		# loop through persistable properties and save in applicable data structure
		for p in self.properties:
			v = getattr(self.saved, p)
			if 'save' in dir(v):
				v.save()
				db.hset(self.entity+":"+p, self.saved.id, v.id)
			else:
				method = 'execute'+type(v).__name__
				try:
					getattr(self, method)(db, p, v)
				except AttributeError:
					print "Cannot save property "+str(p)+" of "+self.entity
	
	def executestr(self, db, prop, val):
		db.hset(self.saved.id, prop, val)

	def executeint(self, db, prop, val):
		db.hset(self.saved.id, prop, val)
	
	def executelist(self, db, prop, val):
		for i, k in enumerate(val):
			if 'save' in dir(k):
				k.save()
				db.hset(self.entity+":"+prop, self.saved.id, k.id)
			else:
				db.hset(self.saved.id+':list:'+prop, i, str(k))
	
	def executedict(self, db, prop, val):
		for i, k in val.iteritems():
			db.hset(self.saved.id+':dict:'+prop, i, str(k))
	
	@staticmethod
	def saveUser(user):
		Save(user, user.persistibleProperties).execute()
		from db import Db
		db = Db()
		db.conn.hset('Users', user.name, user.id)
		db.conn.hset('UserRooms', user.id, user.room.getFullID())
		db.conn.hset('UserRaces', user.id, user.race.name)

	@staticmethod
	def getRandomID():
		return hashlib.sha224(str(time.time())+":"+str(randint(0, 1000000))).hexdigest()
