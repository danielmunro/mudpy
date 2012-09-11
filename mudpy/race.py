from attributes import Attributes

class Race(object):
	SIZE_TINY = 1
	SIZE_SMALL = 2
	SIZE_NORMAL = 3
	SIZE_LARGE = 4
	SIZE_GIGANTIC = 5

	def __init__(self):
		self.name = "critter"
		self.attributes = Attributes()
		self.abilities = []
		self.size = self.SIZE_NORMAL
		self.affects = []
		self.isPlayable = False
		self.movementCost = 1
		self.proficiencies = []
		self.setup();

	def __str__(self):
		return self.name

class Human(Race):
	def setup(self):
		self.name = "human"
		self.isPlayable = True

class Elf(Race):
	def setup(self):
		self.name = "elf"
		self.isPlayable = True

class Dwarf(Race):
	def setup(self):
		self.name = "dwarf"
		self.inPlayable = True
		self.abilities.append("berserk")
		self.size = self.SIZE_SMALL

		# attributes
		self.attributes.hp += 10
		self.attributes.str += 3
		self.attributes.int -= 1
		self.attributes.wis += 1
		self.attributes.dex -= 2
		self.attributes.con += 3
		self.attributes.cha -= 3
