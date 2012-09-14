from attributes import Attributes
from item import Inventory
from save import Save

class Actor(object):
	def __init__(self):
		self.id = Save.getRandomID()
		self.name = "an actor"
		self.long = "An actor is here"
		self.level = 0
		self.experience = 0
		self.attributes = self.getDefaultAttributes()
		self.max_attributes = self.getDefaultAttributes()
		self.sex = "neutral"
		self.room = None
		self.abilities = []
		self.affects = []
		self.target = None
		self.inventory = Inventory()
		self.race = None
		self.proficiencies = dict((proficiency, 15) for proficiency  in ['melee', 'hand to hand', 'curative', 'healing', 'light armor', 'heavy armor', 'slashing', 'piercing', 'bashing', 'staves', 'sneaking', 'evasive', 'maladictions', 'benedictions', 'sorcery'])
		self.equipped = dict((position, None) for position in ['light', 'finger0', 'finger1', 'neck0', 'neck1', 'body', 'head', 'legs', 'feet', 'hands', 'arms', 'torso', 'waist', 'wrist0', 'wrist1', 'wield0', 'wield1', 'float'])
	
	def getMovementCost(self):
		return self.race.movementCost + 1 if self.isEncumbered() else self.race.movementCost
	
	def getMaxWeight(self):
		return 100+(self.level*100)
	
	def isEncumbered(self):
		return self.inventory.getWeight() > self.getMaxWeight() * 0.95
	
	def notify(self, message):
		return
	
	def tick(self):
		self.setAttribute('hp', self.getAttribute('hp') + self.getMaxAttribute('hp') * 0.1)
		self.setAttribute('mana', self.getAttribute('mana') + self.getMaxAttribute('mana') * 0.1)
		self.setAttribute('movement', self.getAttribute('movement') + self.getMaxAttribute('movement') * 0.1)
	
	def setAttribute(self, attribute, value):
		maxatt = self.getMaxAttribute(attribute)
		setattr(self.attributes, attribute, value) if getattr(self.attributes, attribute) + value <= maxatt else setattr(self.attributes, attribute, maxatt)

	def getAttribute(self, attribute):
		calculatedMaxAttribute = self.getMaxAttribute(attribute)
		calculatedAttribute = self.getCalculatedAttribute(self.attributes, attribute)

		return calculatedAttribute if calculatedAttribute < calculatedMaxAttribute else calculatedMaxAttribute
	
	def getMaxAttribute(self, attribute):
		return self.getCalculatedAttribute(self.max_attributes, attribute)
	
	def getBaseAttribute(self, attribute):
		return getattr(self.race.attributes, attribute) + getattr(self.attributes, attribute)
		
	def getCalculatedAttribute(self, attributes, attribute):
		# affects and race modifiers
		def getAtt(affect): return getattr(affect.attributes, attribute)
		modifiers = sum(map(getAtt, self.affects)) + getattr(self.race.attributes, attribute)

		# base attributes + modifiers
		return getattr(attributes, attribute) + modifiers
	
	def save(self):
		Save(self, ['id', 'name', 'level', 'experience', 'attributes', 'max_attributes', 'sex', 'room', 'abilities', 'inventory']).execute()
	
	def getAbilities(self):
		return self.abilities + self.race.abilities

	def __str__(self):
		return self.name
	
	def getDefaultAttributes(self):
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
		a.str = 15
		a.int = 15
		a.wis = 15
		a.dex = 15
		a.con = 15
		a.cha = 15
		return a
	
class Mob(Actor):
	def __init__(self):
		self.movement = 1
		self.respawn = 1
		self.auto_flee = False
		self.area = None
		self.role = ''
		super(Mob, self).__init__()

class User(Actor):
	def prompt(self):
		return "%i %i %i >> " % (self.getAttribute('hp'), self.getAttribute('mana'), self.getAttribute('movement'))
	
	def notify(self, message):
		self.client.write(message)
	
	def tick(self):
		super(User, self).tick()
		self.notify("\n\n"+self.prompt())
