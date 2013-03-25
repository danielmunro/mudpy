from parser import Parser

class AffectParser(Parser):
	def __init__(self):
		super(AffectParser, self).__init__('affects', self.parseAffect, self.parseJsonAffect)
	
	def parseAffect(self, _class):
		from mudpy.affect import Affect
		Parser._globals.append(self.applyDefinitionsTo(locals()[_class]()))
	
	def parseJsonAffect(self): pass
