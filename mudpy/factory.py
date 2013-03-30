from mudpy.utility import *
from mudpy.race import Race
from mudpy.ability import Ability
from mudpy.command import *
from mudpy.room import *
from mudpy.proficiency import Proficiency
from mudpy.affect import Affect
import copy, inspect

class Factory:
	@staticmethod
	def new(scalar = True, newWith = None, **kwargs):
		from mudpy.parser import Parser
		lookups = []
		for _type, _class in kwargs.iteritems():
			lookup = startsWith(_class, globals()[_type].__subclasses__(), Parser._globals, Ability.instances);
			if lookup:
				lookups.append(lookup)
			else:
				raise NameError("Factory cannot create a new instance of: "+_type+"."+_class)
		if scalar and len(lookups) == 1:
			class_ = lookups[0]
			if inspect.isclass(class_):
				return class_(newWith) if newWith else class_()
			return copy.copy(class_)
		return lookups
