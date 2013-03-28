from mudpy.parser.parser import Parser

class RaceParser(Parser):
	def __init__(self):
		super(RaceParser, self).__init__('races', self.parseRace, self.parseJsonRace)
	
	def parseRace(self, _class): pass
	
	def parseJsonRace(self, parent, instance):
		Parser._globals.append(instance)
