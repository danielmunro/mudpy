from parser import Parser

class AbilityParser(Parser):
	def __init__(self):
		super(AbilityParser, self).__init__('abilities', self.parseAbility)
	
	def parseAbility(self, _class):
		from mudpy.ability import Ability
		Ability.instances.append(self.applyDefinitionsTo(locals()[_class]()))
