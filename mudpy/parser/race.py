from mudpy.parser.parser import Parser

class RaceParser(Parser):
	def __init__(self):
		super(RaceParser, self).__init__('races', self.parseRace, self.parseJsonRace)
	
	def parseRace(self, _class):
		from mudpy.race import Race
		Parser._globals.append(self.applyDefinitionsTo(locals()[_class]()))
	
	def parseJsonRace(self, instance):
		Parser._globals.append(instance)
