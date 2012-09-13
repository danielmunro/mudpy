from attributes import Attributes
from ability import AbilityFactory

class Race(object):
	SIZE_TINY = 1
	SIZE_SMALL = 2
	SIZE_NORMAL = 3
	SIZE_LARGE = 4
	SIZE_GIGANTIC = 5
	name = "critter"
	size = SIZE_NORMAL
	movementCost = 1
	isPlayable = False
	proficiencies = []

	def __init__(self):
		self.attributes = Attributes()
		self.abilities = []
		self.affects = []
		self.setup();
	
	def setup(self):
		pass

	def __str__(self):
		return self.name

class RaceFactory:
	races = []

	@staticmethod
	def newRace(name):
		TypeType = type(type)
		for race in Race.__subclasses__():
			if getattr(race, 'name') == name:
				return race()
	
	@staticmethod
	def getRaces():
		if not RaceFactory.races:
			RaceFactory.races = RaceFactory.initializeAllRaces()
		return RaceFactory.races
	
	@staticmethod
	def initializeAllRaces():
		TypeType = type(type)
		races = []
		for race in Race.__subclasses__():
			races.append(race())
		return races


class Human(Race):
	name = "human"
	isPlayable = True

class Elf(Race):
	name = "elf"
	isPlayable = True
	proficiencies = {'light armor': 5, 'piercing': 5, 'sorcery': 5, 'sneaking': 5, 'evasive': 5}

	def setup(self):
		self.abilities.append(AbilityFactory.newAbility("sneak"))

		# attributes
		self.attributes.str -= 3
		self.attributes.int += 2
		self.attributes.wis += 1
		self.attributes.dex += 2
		self.attributes.con -= 3

class Dwarf(Race):
	name = "dwarf"
	inPlayable = True
	proficiencies = {'melee': 10, 'slashing': 5, 'heavy armor': 5}
	size = Race.SIZE_SMALL

	def setup(self):
		self.abilities.append(AbilityFactory.newAbility("berserk"))

		# attributes
		self.attributes.str += 3
		self.attributes.int -= 1
		self.attributes.wis += 1
		self.attributes.dex -= 2
		self.attributes.con += 3
		self.attributes.cha -= 3
