from db import Db

class Save:
	def __init__(self, saved, properties):
		self.saved = saved
		self.properties = properties
		self.entity = saved.__class__.__name__
	
	def execute(self):
		# get connection
		db = Db().getConnection()
		# save the object's id in the entity set
		db.sadd(self.entity, self.saved.id)
		# loop through persistable properties and save in applicable data structure
		for p in self.properties:
			v = getattr(self.saved, p)
			t = type(v)
			if t is str:
				db.hset(self.saved.id, p, v)
			elif t is int:
				db.hset(self.saved.id, p, str(v))
			elif t is list:
				for i, k in enumerate(v):
					if k:
						db.hset(self.saved.id+':'+p, i, str(k))
			elif 'save' in dir(v):
				from room import Room
				if not v is Room:
					v.save()
				db.sadd(self.entity+":"+v.__class__.__name__, p, v.id)
			else:
				pass
		
