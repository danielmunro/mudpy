from attributes import Attributes

class Race:
	SIZE_TINY = 1
	SIZE_SMALL = 2
	SIZE_NORMAL = 3
	SIZE_LARGE = 4
	SIZE_GIGANTIC = 5

	def __init__(self):
		self.name = "critter"
		self.size = self.SIZE_NORMAL
		self.movementCost = 1
		self.isPlayable = False
		self.damType = "bash"
		self.proficiencies = {}
		self.attributes = Attributes()
		self.abilities = []
		self.affects = []
	
	def addProficiency(self, proficiency, level):
		try:
			self.proficiencies[proficiency].level += level
		except KeyError:
			from factory import Factory
			from proficiency import Proficiency
			self.proficiencies[proficiency] = Factory.newFromWireframe(Proficiency(), proficiency)
			self.proficiencies[proficiency].level = level

	def __str__(self):
		return self.name
