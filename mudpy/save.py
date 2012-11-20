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
				method = 'execute'+type(v).__name__;
				try:
					getattr(self, method)(db, p, v);
				except AttributeError:
					print "Cannot save property "+str(p)+" of "+self.entity
	
	def executestr(self, db, prop, val):
		db.hset(self.saved.id, prop, val)

	def executeint(self, db, prop, val):
		db.hset(self.saved.id, prop, val)
	
	def executelist(self, db, prop, val):
		for i, k in enumerate(val):
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
		db.conn.hset('Users', user.id+':room', user.room.getFullID())
	
	@staticmethod
	def loadUser(name):
		db = Db().conn
		userid = db.hget('Users', name)
		user = None
		if userid:
			from actor import User
			from client import ClientFactory
			from factory import Factory
			from room import Room
			user = User()
			properties = db.hgetall(userid)
			for property, value in properties.iteritems():
				setattr(user, property, value)
			raceid = db.hget('User:race', userid)
			racename = db.hget(raceid, 'name')
			user.race = Factory.new(Race = racename)
			roomid = db.hget('Users', userid+':room')
			user.room = Room.rooms[roomid]
		return user

	@staticmethod
	def getRandomID():
		return hashlib.sha224(str(time.time())+":"+str(randint(0, 1000000))).hexdigest()
