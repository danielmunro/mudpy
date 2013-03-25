from parser import Parser

class ProficiencyParser(Parser):
	def __init__(self):
		super(ProficiencyParser, self).__init__('proficiencies', self.parseProficiency, self.parseJsonProficiency)
	
	def parseProficiency(self, _class):
		from mudpy.proficiency import Proficiency
		prof = self.applyDefinitionsTo(locals()[_class]())
		if prof.hook in dir(Proficiency):
			Parser._globals.append(prof)
		else:
			from mudpy.debug import Debug
			Debug.log(prof.hook+' hook does not exist', 'error')
	
	def parseJsonProficiency(self): pass
