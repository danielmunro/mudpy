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
	damType = 'bash'

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

class Faerie(Race):
	name = "faerie"
	isPlayable = True
	size = Race.SIZE_TINY
	proficiencies = {'evasive': 5, 'maladictions': 10, 'sorcery': 10}

	def setup(self):
		from factory import Factory
		#self.abilities.append(Factory.new(Ability = "dirt kick", Ability = "kick"))

		# attributes
		self.attributes.str += 3
		self.attributes.int -= 2
		self.attributes.wis += 2
		self.attributes.dex += 0
		self.attributes.con += 3
		self.attributes.cha -= 3

class Giant(Race):
	name = "giant"
	isPlayable = True
	size = Race.SIZE_GIGANTIC
	proficiencies = {'bashing': 5, 'alchemy': 5, 'melee': 5, 'elemental': 5}

	def setup(self):
		from factory import Factory
		#self.abilities.append(Factory.new(Ability = "dirt kick", Ability = "kick"))

		# attributes
		self.attributes.str += 3
		self.attributes.int -= 2
		self.attributes.wis += 2
		self.attributes.dex += 0
		self.attributes.con += 3
		self.attributes.cha -= 3

class Ogre(Race):
	name = "ogre"
	isPlayable = True
	size = Race.SIZE_LARGE
	proficiencies = {'melee': 10, 'bashing': 10, 'heavy armor': 5}

	def setup(self):
		from factory import Factory
		self.abilities.append(Factory.new(Ability = "bash"))

		# attributes
		self.attributes.str += 3
		self.attributes.int -= 2
		self.attributes.wis += 2
		self.attributes.dex += 0
		self.attributes.con += 3
		self.attributes.cha -= 3

class Volare(Race):
	name = "volare"
	isPlayable = True
	proficiencies = {'curative': 10, 'healing': 10}

	def setup(self):

		# attributes
		self.attributes.str -= 2
		self.attributes.int += 1
		self.attributes.wis += 3
		self.attributes.dex += 0
		self.attributes.con -= 2

class Gnome(Race):
	name = "gnome"
	isPlayable = True
	size = Race.SIZE_SMALL
	proficiencies = {'evasive': 5, 'sneaking': 10, 'maladictions': 5, 'sorcery': 5}

	def setup(self):
		from factory import Factory
		#self.abilities.append(Factory.new(Ability = "sneak", Ability = "dirt kick"))

		# attributes
		self.attributes.str -= 4
		self.attributes.int += 3
		self.attributes.wis += 2
		self.attributes.dex += 2
		self.attributes.con -= 3

class Elf(Race):
	name = "elf"
	isPlayable = True
	proficiencies = {'light armor': 5, 'piercing': 5, 'sorcery': 5, 'sneaking': 5, 'evasive': 5}
	size = Race.SIZE_SMALL

	def setup(self):
		from factory import Factory
		self.abilities.append(Factory.new(Ability = "sneak"))

		# attributes
		self.attributes.str -= 3
		self.attributes.int += 2
		self.attributes.wis += 1
		self.attributes.dex += 3
		self.attributes.con -= 3

class Kobold(Race):
	name = "kobold"
	isPlayable = False
	proficiencies = {'light armor': 5, 'piercing': 5, 'sorcery': 5, 'sneaking': 5, 'evasive': 5}
	size = Race.SIZE_SMALL

	def setup(self):
		from factory import Factory
		self.abilities.append(Factory.new(Ability = "sneak"))

		# attributes
		self.attributes.str -= 3
		self.attributes.int += 2
		self.attributes.wis += 1
		self.attributes.dex += 3
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
