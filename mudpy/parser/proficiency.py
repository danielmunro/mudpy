from parser import Parser

class ProficiencyParser(Parser):
	def __init__(self):
		super(ProficiencyParser, self).__init__('proficiencies', self.parseProficiency)
	
	def parseProficiency(self, _class):
		from mudpy.proficiency import Proficiency
		Parser._globals.append(self.applyDefinitionsTo(locals()[_class]()))
