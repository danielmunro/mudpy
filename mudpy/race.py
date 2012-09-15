from attributes import Attributes

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

class Human(Race):
	name = "human"
	isPlayable = True

class Giant(Race):
	name = "giant"
	isPlayable = True

class Ogre(Race):
	name = "ogre"
	isPlayable = True

class Volare(Race):
	name = "volare"
	isPlayable = True

class Gnome(Race):
	name = "gnome"
	isPlayable = True

class Elf(Race):
	name = "elf"
	isPlayable = True
	proficiencies = {'light armor': 5, 'piercing': 5, 'sorcery': 5, 'sneaking': 5, 'evasive': 5}

	def setup(self):
		from factory import Factory
		self.abilities.append(Factory.new(Ability = "sneak"))

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
		from factory import Factory
		self.abilities.append(Factory.new(Ability = "berserk"))

		# attributes
		self.attributes.str += 3
		self.attributes.int -= 1
		self.attributes.wis += 1
		self.attributes.dex -= 2
		self.attributes.con += 3
		self.attributes.cha -= 3
