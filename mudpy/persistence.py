import time, hashlib
from random import randint
from db import Db

class Load:

	def __init__(self, loaded, properties):
		self.loaded = loaded
		self.properties = properties
		self.entity = loaded.__class__.__name__
	
	def execute(self):
		# get connection
		db = Db().conn

		for p in self.properties:
			v = getattr(self.loaded, p)
			if 'load' in dir(v):
				v.id = db.hget(self.entity+":"+p, self.loaded.id)
				v.load()
			else:
				method = 'execute'+type(v).__name__
				try:
					if p == 'items':
						items = getattr(self, method)(self.loaded.id, db, p)
						for i in items:
							self.loaded.append(i)
					else:
						setattr(self.loaded, p, getattr(self, method)(self.loaded.id, db, p))
				except AttributeError:
					print "Cannot load property "+str(p)+" of "+str(self.loaded)+" using method "+method
	
	@staticmethod
	def loadUser(name):
		db = Db().conn
		userid = db.hget('Users', name)
		user = None
		if userid:
			from race import Race
			from actor import User
			from client import ClientFactory
			from factory import Factory
			from room import Room
			user = User()
			user.id = userid
			Load(user, user.persistibleProperties).execute()

			# race
			racename = db.hget('UserRaces', userid)
			user.race = Factory.newFromWireframe(Race(user), racename)

			# room
			roomid = db.hget('UserRooms', userid)
			user.room = Room.rooms[roomid]
			user.room.actors.append(user)
		return user

	def executestr(self, userid, db, prop):
		return db.hget(userid, prop);
	
	def executeint(self, userid, db, prop):
		return int(db.hget(userid, prop) or 0);

	def executelist(self, userid, db, prop):
		l = list()
		for value in db.smembers(userid+':list:'+prop):
			t = db.get(value+":type")
			toAdd = globals()[t]()
			toAdd.id = value
			toAdd.load()
			l.append(toAdd)
		return l

		#return list(value for key, value in db.hgetall(userid+':list:'+prop).iteritems())

	def executedict(self, userid, db, prop):
		return dict((key, value) for key, value in db.hgetall(userid+':dict:'+prop).iteritems())

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
