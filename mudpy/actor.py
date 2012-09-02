from attributes import Attributes

class Actor(object):
	def __init__(self, name):
		self.name = name
		self.experience = 0
		self.attributes = self.getDefaultAttributes()
		self.max_attributes = self.getDefaultAttributes()
	
	def notify(self, message):
		return
	
	def tick(self):
		print "tick"

	def __str__(self):
		return self.name
	
	def getDefaultAttributes()
		a = Attributes()
		a.hp = 20
		a.mana = 20
		a.movement = 100
		a.ac_bash = 100
		a.ac_pierce = 100
		a.ac_slash = 100
		a.ac_magic = 100
		a.hit = 1
		a.dam = 1
		return a

class Mob(Actor):
	movement = 1

class User(Actor):
	def __init__(self, client, name):
		self.client = client
		super(User, self).__init__(name)

	def look(self):
		self.client.write("%s\n%s\n[Exits %s]\n%s" % (self.room.title, self.room.description, self.room.getDirectionString(), self.room.getActorsString(self)))
	
	def prompt(self):
		return ">> "
	
	def notify(self, message):
		self.client.write(message)
