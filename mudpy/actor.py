from __future__ import division
from attributes import Attributes
from item import Inventory
from save import Save
from random import choice
from room import Direction
from heartbeat import Heartbeat

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
		self.disposition = Disposition.STANDING
		self.proficiencies = dict((proficiency, 15) for proficiency  in ['melee', 'hand to hand', 'curative', 'healing', 'light armor', 'heavy armor', 'slashing', 'piercing', 'bashing', 'staves', 'sneaking', 'evasive', 'maladictions', 'benedictions', 'sorcery', 'haggling', 'alchemy', 'elemental'])
		self.equipped = dict((position, None) for position in ['light', 'finger0', 'finger1', 'neck0', 'neck1', 'body', 'head', 'legs', 'feet', 'hands', 'arms', 'torso', 'waist', 'wrist0', 'wrist1', 'wield0', 'wield1', 'float'])

		Heartbeat.instance.attach('tick', self)
	
	def getEquipmentByPosition(self, position):
		for _position in self.equipped:
			if _position.find(position) == 0:
				return self.equipped[_position]
	
	def setEquipment(self, equipment):
		return self.setEquipmentByPosition(equipment.position, equipment)
	
	def setEquipmentByPosition(self, position, equipment):
		for _position in self.equipped:
			if _position.find(position) == 0:
				self.equipped[_position] = equipment
				return True
		return False
	
	def getMovementCost(self):
		return self.race.movementCost + 1 if self.isEncumbered() else self.race.movementCost
	
	def getMaxWeight(self):
		return 100+(self.level*100)
	
	def isEncumbered(self):
		return self.inventory.getWeight() > self.getMaxWeight() * 0.95
	
	def notify(self, message):
		return
	
	def tick(self):
		modifier = 0.1 if self.disposition != Disposition.INCAPACITATED else -0.1
		self.trySetAttribute('hp', self.getAttribute('hp') + self.getMaxAttribute('hp') * modifier)
		self.trySetAttribute('mana', self.getAttribute('mana') + self.getMaxAttribute('mana') * modifier)
		self.trySetAttribute('movement', self.getAttribute('movement') + self.getMaxAttribute('movement') * modifier)
	
	def pulse(self):
		if self.target and not self.target.target:
			self.target.target = self
			Heartbeat.instance.attach('pulse', self.target)
		elif not self.target:
			Heartbeat.instance.detach('pulse', self)

		self.doRegularAttacks()
	
	def postPulse(self):
		pass
	
	def trySetAttribute(self, attributeName, amount):
		maxAttributeAmount = self.getMaxAttribute(attributeName)
		amount = amount if amount < maxAttributeAmount else maxAttributeAmount
		setattr(self.attributes, attributeName, amount)  

	def getAttribute(self, attributeName):
		amount = self.getCalculatedAttribute(attributeName, self.attributes, self.race.attributes)
		for affect in self.affects:
			amount += getattr(affect.attributes, attributeName)
		return min(amount, self.getMaxAttribute(attributeName))

	def getMaxAttribute(self, attributeName):
		return self.getCalculatedAttribute(attributeName, self.max_attributes, self.race.attributes)

	def getCalculatedAttribute(self, attributeName, *attributes):
		amount = 0
		for attribute in attributes:
			amount += getattr(attribute, attributeName)
		return amount;
	
	def save(self):
		Save(self, ['id', 'name', 'level', 'experience', 'attributes', 'max_attributes', 'sex', 'room', 'abilities', 'inventory']).execute()
	
	def getAbilities(self):
		return self.abilities + self.race.abilities

	def __str__(self):
		return self.name
	
	def getWieldedWeapons(self):
		return list(equipment for equipment in [self.equipped['wield0'], self.equipped['wield1']] if equipment)
	
	def doRegularAttacks(self, recursedAttackIndex = 0):
		if not self.target:
			Heartbeat.instance.detach('pulse', self)
			return

		if self.disposition != Disposition.INCAPACITATED:
			regularattacks = ['reg']
			try:
				Attack(self, regularattacks[recursedAttackIndex])
				self.doRegularAttacks(recursedAttackIndex + 1)
			except IndexError:
				pass
	
	def status(self):
		hppercent = self.getAttribute('hp') / self.getMaxAttribute('hp')
		
		if hppercent < 0.1:
			description = 'is in awful condition'
		elif hppercent < 0.15:
			description = 'looks pretty hurt'
		elif hppercent < 0.30:
			description = 'has some big nasty wounds and scratches'
		elif hppercent < 0.50:
			description = 'has quite a few wounds'
		elif hppercent < 0.75:
			description = 'has some small wounds and bruises'
		elif hppercent < 0.99:
			description = 'has a few scratches'
		else:
			description = 'is in excellent condition'

		return str(self).title()+' '+description+'.'
	
	def move(self, direction = ""):
		from factory import Factory
		Factory.new(MoveDirection = direction if direction else choice(list(d for d in self.room.directions if d))).tryPerform(self)
	
	def die(self):
		self.removeFromBattle()
		self.disposition = Disposition.LAYING
		setattr(self.attributes, 'hp', 1)
	
	def removeFromBattle(self):
		if self.target and self.target.target is self:
			self.target.target = None

		if self.target:
			self.target = None
	
	@staticmethod
	def getDamageVerb(dam_roll):
		if dam_roll < 5:
			return "clumsy"
		elif dam_roll < 10:
			return "amateur"
		elif dam_roll < 15:
			return "competent"
		else:
			return "skillful"

	@staticmethod
	def getDefaultAttributes():
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
		self.movement_timeout = 1
		self.movement_timer = self.movement_timeout
		self.respawn = 1
		self.auto_flee = False
		self.area = None
		self.role = ''
		super(Mob, self).__init__()
	
	def tick(self):
		super(Mob, self).tick()
		if self.movement_timeout:
			self.decrementMovementTimer()
	
	def decrementMovementTimer(self):
		self.movement_timer -= 1;
		if self.movement_timer < 0:
			self.move()
			self.movement_timer = self.movement_timeout
	
	def trySetAttribute(self, attribute, value):
		if attribute == 'hp':
			if value < 0:
				self.die()
				return

		super(Mob, self).trySetAttribute(attribute, value)
	
	def die(self):
		super(Mob, self).die()
		self.room.announce({
			"*": str(self).title()+" arrives in a puff of smoke."
		})
	
class User(Actor):
	def prompt(self):
		return "%i %i %i >> " % (self.getAttribute('hp'), self.getAttribute('mana'), self.getAttribute('movement'))
	
	def notify(self, message):
		self.client.write(message)
	
	def tick(self):
		super(User, self).tick()
		self.notify("\n"+self.prompt())
	
	def postPulse(self):
		if self.target:
			self.notify(self.target.status()+"\n")
			self.notify("\n"+self.prompt())
	
	def trySetAttribute(self, attribute, value):
		if attribute == 'hp':
			curhp = self.getAttribute('hp')
			if value < -9:
				self.die()
				return
			elif value <= 0 and curhp > 0:
				self.disposition = Disposition.INCAPACITATED
				self.notify("You are incapacitated and will slowly die if not aided.\n")
			elif curhp <= 0 and value > 0:
				self.disposition = Disposition.LAYING

		super(User, self).trySetAttribute(attribute, value)

	
	def die(self):
		super(User, self).die()
		self.room.actors.remove(self)
		from room import Room
		self.room = Room.rooms["midgaard:82"]
		self.room.actors.append(self)
		self.room.announce({
			self: "You feel a rejuvinating rush as you pass through this mortal plane.",
			"*": str(self).title()+" arrives in a puff of smoke."
		})
		self.notify("\n"+self.prompt())

class Disposition:
	STANDING = 'standing'
	SITTING = 'sitting'
	LAYING = 'laying'
	SLEEPING = 'sleeping'
	INCAPACITATED = 'incapacitated'

class Attack:
	def __init__(self, aggressor, attackname):
		from random import uniform

		# initial rolls for attack/defense
		hit_roll = aggressor.getAttribute('hit') + self.getAttributeModifier(aggressor, 'dex')
		def_roll = self.getAttributeModifier(aggressor.target, 'dex')
		def_roll += 5 - aggressor.target.race.size

		# determine dam type from weapon
		weapons = aggressor.getWieldedWeapons()
		try:
			damType = weapons[0].damageType
		except IndexError:
			damType = aggressor.race.damType

		# get the ac bonus from the damage type
		try:
			ac = aggressor.target.getAttribute('ac_'+damType) / 100
		except AttributeError:
			ac = 0

		# roll the dice and determine if the attack was successful
		roll = uniform(hit_roll/2, hit_roll) - uniform(def_roll/2, def_roll) - ac
		if roll > 0:
			isHit = "hits"
			dam_roll = aggressor.getAttribute('dam') + self.getAttributeModifier(aggressor, 'str')
			dam_roll = uniform(dam_roll/2, dam_roll)
		else:
			isHit = "misses"
			dam_roll = 0

		# update the room on the attack progress
		verb = Actor.getDamageVerb(dam_roll)
		ucname = str(aggressor).title()
		tarname = str(aggressor.target)
		aggressor.room.announce({
			aggressor: "("+attackname+") Your "+verb+" attack "+isHit+" "+tarname+".",
			aggressor.target: ucname+"'s "+verb+" attack "+isHit+" you.",
			"*": ucname+"'s "+verb+" attack "+isHit+" "+tarname+"."
		})

		#need to do this check again here, can't have the actor dead before the hit message
		if roll > 0: 
			aggressor.target.trySetAttribute('hp', aggressor.target.getAttribute('hp') - dam_roll)
	
	def getAttributeModifier(self, actor, attributeName):
		return (actor.getAttribute(attributeName) / Attributes.MAX_ATTRIBUTE) * 4
