import time, hashlib, random, redis

def db():
	return redis.Redis(host='localhost', port=6379, db=10)

def loadUser(name):
	conn = db()
	userid = conn.hget('Users', name)
	user = None
	if userid:
		import factory
		from actor import User, Race
		from client import ClientFactory
		from room import Room
		user = User()
		user.id = userid
		load(user, user.persistibleProperties)

		# race
		racename = conn.hget('UserRaces', userid)
		user.race = factory.new(Race(), racename)

		# room
		roomid = conn.hget('UserRooms', userid)
		user.room = Room.rooms[roomid]
		user.room.actors.append(user)
	return user

def saveUser(user):
	save(user, user.persistibleProperties)
	conn = db()
	conn.hset('Users', user.name, user.id)
	conn.hset('UserRooms', user.id, user.room.getFullID())
	conn.hset('UserRaces', user.id, user.race.name)
	
def getRandomID():
	return hashlib.sha224(str(time.time())+":"+str(random.randint(0, 1000000))).hexdigest()

def load(loaded, properties):
	# get connection
	conn = db()
	entity = loaded.__class__.__name__

	for p in properties:
		v = getattr(loaded, p)
		if 'load' in dir(v):
			v.id = conn.hget(entity+":"+p, loaded.id)
			v.load()
		else:
			method = '_load'+type(v).__name__
			try:
				if p == 'items':
					items = globals()[method](loaded.id, conn, p)
					for i in items:
						loaded.append(i)
				else:
					setattr(loaded, p, globals()[method](loaded.id, conn, p))
			except AttributeError:
				print "Cannot load property "+str(p)+" of "+str(loaded)+" using method "+method

def _loadstr(userid, conn, prop):
	return conn.hget(userid, prop);

def _loadint(userid, conn, prop):
	return int(conn.hget(userid, prop) or 0);

def _loadlist(userid, conn, prop):
	l = list()
	for value in conn.smembers(userid+':list:'+prop):
		t = conn.get(value+":type")
		toAdd = globals()[t]()
		toAdd.id = value
		toAdd.load()
		l.append(toAdd)
	return l

def _loaddict(userid, conn, prop):
	return dict((key, value) for key, value in conn.hgetall(userid+':dict:'+prop).iteritems())

def save(saved, properties):
	# get connection
	conn = db()
	entity = saved.__class__.__name__

	# ensure the object has an id
	if not saved.id:
		saved.id = getRandomID()

	# save the object's id in the entity set
	conn.sadd(entity, saved.id)

	# loop through persistable properties and save in applicable data structure
	for p in properties:
		v = getattr(saved, p)
		if 'save' in dir(v):
			v.save()
			conn.hset(entity+":"+p, saved.id, v.id)
		else:
			method = 'save'+type(v).__name__
			try:
				globals()[method](saved, conn, p, v)
			except AttributeError:
				print "Cannot save property "+str(p)+" of "+entity
	
def _savestr(saved, conn, prop, val):
	conn.hset(saved.id, prop, val)

def _saveint(saved, conn, prop, val):
	conn.hset(saved.id, prop, val)

def _savelist(saved, conn, prop, val):
	for i, k in enumerate(val):
		if 'save' in dir(k):
			k.save()
			conn.hset(entity+":"+prop, saved.id, k.id)
		else:
			conn.hset(saved.id+':list:'+prop, i, str(k))

def _savedict(saved, conn, prop, val):
	for i, k in val.iteritems():
		conn.hset(saved.id+':dict:'+prop, i, str(k))
