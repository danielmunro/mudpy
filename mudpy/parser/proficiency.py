from parser import Parser

class ProficiencyParser(Parser):
	def __init__(self):
		super(ProficiencyParser, self).__init__('proficiencies', self.parseProficiency, self.parseJsonProficiency)
	
	def parseProficiency(self, _class): pass
	
	def parseJsonProficiency(self, parent, instance):
		Parser._globals.append(instance)
