import time, hashlib, random, redis

def db():
	return redis.Redis(host='localhost', port=6379, db=10)

def loadUser(name):
	conn = db()
	userid = conn.hget('Users', name)
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
		racename = conn.hget('UserRaces', userid)
		user.race = Factory.newFromWireframe(Race(), racename)

		# room
		roomid = conn.hget('UserRooms', userid)
		user.room = Room.rooms[roomid]
		user.room.actors.append(user)
	return user

def saveUser(user):
	Save(user, user.persistibleProperties).execute()
	conn = db()
	conn.hset('Users', user.name, user.id)
	conn.hset('UserRooms', user.id, user.room.getFullID())
	conn.hset('UserRaces', user.id, user.race.name)

class Load:

	def __init__(self, loaded, properties):
		self.loaded = loaded
		self.properties = properties
		self.entity = loaded.__class__.__name__
	
	def execute(self):
		# get connection
		conn = db()

		for p in self.properties:
			v = getattr(self.loaded, p)
			if 'load' in dir(v):
				v.id = conn.hget(self.entity+":"+p, self.loaded.id)
				v.load()
			else:
				method = 'execute'+type(v).__name__
				try:
					if p == 'items':
						items = getattr(self, method)(self.loaded.id, conn, p)
						for i in items:
							self.loaded.append(i)
					else:
						setattr(self.loaded, p, getattr(self, method)(self.loaded.id, conn, p))
				except AttributeError:
					print "Cannot load property "+str(p)+" of "+str(self.loaded)+" using method "+method
	
	def executestr(self, userid, conn, prop):
		return conn.hget(userid, prop);
	
	def executeint(self, userid, conn, prop):
		return int(conn.hget(userid, prop) or 0);

	def executelist(self, userid, conn, prop):
		l = list()
		for value in conn.smembers(userid+':list:'+prop):
			t = conn.get(value+":type")
			toAdd = globals()[t]()
			toAdd.id = value
			toAdd.load()
			l.append(toAdd)
		return l

	def executedict(self, userid, conn, prop):
		return dict((key, value) for key, value in conn.hgetall(userid+':dict:'+prop).iteritems())

class Save:
	def __init__(self, saved, properties):
		self.saved = saved
		self.properties = properties
		self.entity = saved.__class__.__name__
	
	def execute(self):
		# get connection
		conn = db()

		# ensure the object has an id
		if not self.saved.id:
			self.saved.id = self.getRandomID()

		# save the object's id in the entity set
		conn.sadd(self.entity, self.saved.id)

		# loop through persistable properties and save in applicable data structure
		for p in self.properties:
			v = getattr(self.saved, p)
			if 'save' in dir(v):
				v.save()
				conn.hset(self.entity+":"+p, self.saved.id, v.id)
			else:
				method = 'execute'+type(v).__name__
				try:
					getattr(self, method)(conn, p, v)
				except AttributeError:
					print "Cannot save property "+str(p)+" of "+self.entity
	
	def executestr(self, conn, prop, val):
		conn.hset(self.saved.id, prop, val)

	def executeint(self, conn, prop, val):
		conn.hset(self.saved.id, prop, val)
	
	def executelist(self, conn, prop, val):
		for i, k in enumerate(val):
			if 'save' in dir(k):
				k.save()
				conn.hset(self.entity+":"+prop, self.saved.id, k.id)
			else:
				conn.hset(self.saved.id+':list:'+prop, i, str(k))
	
	def executedict(self, conn, prop, val):
		for i, k in val.iteritems():
			conn.hset(self.saved.id+':dict:'+prop, i, str(k))
	
	@staticmethod
	def getRandomID():
		return hashlib.sha224(str(time.time())+":"+str(random.randint(0, 1000000))).hexdigest()
