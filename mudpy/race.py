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
	startingProficiencies = {}
	damType = 'bash'

	def __init__(self, actor = None):
		self.proficiencies = {}
		self.attributes = Attributes()
		self.abilities = []
		self.affects = []
		self.setup();
		if actor:
			from factory import Factory
			for proficiency in self.startingProficiencies:
				level = self.startingProficiencies[proficiency]
				self.proficiencies[proficiency] = Factory.new(Proficiency = proficiency, newWith = actor)
				self.proficiencies[proficiency].level = level
	
	def setup(self):
		pass
	
	def addProficiency(self, proficiency, level):
		try:
			self.proficiencies[proficiency].level += level
		except KeyError:
			from factory import Factory
			self.proficiencies[proficiency] = Factory.new(Proficiency = proficiency)
			self.proficiencies[proficiency].level = level

	def __str__(self):
		return self.name
