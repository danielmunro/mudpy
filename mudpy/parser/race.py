from mudpy.parser.parser import Parser, ParserException

class RaceParser(Parser):
	def __init__(self):
		super(RaceParser, self).__init__('races', 'parseRace')
	
	def parseRace(self, _class):
		from mudpy.race import Race
		instance = locals()[_class]()
		try:
			for chunk in self.definitions[_class]:
				chunk.process(self, instance)
		except ParserException:
			pass
		Parser._globals.append(instance)
