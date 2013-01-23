from mudpy.parser.parser import Parser, ParserException
from mudpy.race import Race

class RaceParser(Parser):
	def __init__(self):
		super(RaceParser, self).__init__('races', 'parseRace')
	
	def parseRace(self, line):
		if line in self.definitions:
			_class = line.strip().title()
			instance = globals()[_class]()
			try:
				for chunk in self.definitions[line]:
					chunk.process(self, instance)
			except ParserException:
				pass
			Parser._globals.append(instance)
