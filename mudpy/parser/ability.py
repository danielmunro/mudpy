from parser import Parser
from mudpy.ability import Ability

class AbilityParser(Parser):
	def __init__(self):
		super(AbilityParser, self).__init__('abilities', self.parseAbility, self.parseJsonAbility)
	
	def parseAbility(self, _class): pass

	def parseJsonAbility(self, instance):
		Ability.instances.append(instance)

