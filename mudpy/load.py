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
			from actor import User
			from client import ClientFactory
			from factory import Factory
			from room import Room
			user = User()
			user.id = userid
			Load(user, user.persistibleProperties).execute()

			# race
			racename = db.hget('UserRaces', userid)
			user.race = Factory.new(Race = racename, newWith = user)

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
