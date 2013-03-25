from parser import Parser

class AffectParser(Parser):
	def __init__(self):
		super(AffectParser, self).__init__('affects', self.parseAffect, self.parseJsonAffect)
	
	def parseAffect(self, _class): pass
	
	def parseJsonAffect(self, instance):
		Parser._globals.append(instance)
