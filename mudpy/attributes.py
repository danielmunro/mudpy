from save import Save

class Attributes(object):
	stats = ['str', 'int', 'wis', 'dex', 'con', 'cha']

	def __init__(self):
		self.hp = 0
		self.mana = 0
		self.movement = 0

		self.saves = 0

		self.ac_bash = 0
		self.ac_pierce = 0
		self.ac_slash = 0
		self.ac_magic = 0

		self.hit = 0
		self.dam = 0

		self.str = 0
		self.int = 0
		self.wis = 0
		self.dex = 0
		self.con = 0
		self.cha = 0
	
	def save(self):
		Save(self, ['id', 'hp', 'mana', 'movement', 'saves', 'ac_bash', 'ac_pierce', 'ac_slash', 'ac_magic', 'hit', 'dam']).execute()

class ActorAttributes(Attributes):
	def __init__(self):
		self.id = Save.getRandomID()
		self.maxhp = 0
		self.maxmana = 0
		self.maxmovement = 0
		super(ActorAttributes, self).__init__()
