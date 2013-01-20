from utility import *
from race import *
from ability import *
from command import *
from room import *
from proficiency import *

class Factory:
	@staticmethod
	def new(scalar = True, newWith = None, **kwargs):
		lookups = []
		for _type, _class in kwargs.iteritems():
			lookup = startsWith(_class, globals()[_type].__subclasses__());
			if lookup:
				lookups.append(lookup(newWith) if newWith else lookup())
			else:
				raise NameError("Factory cannot create a new instance of: "+_type+"."+_class)
		if scalar and len(lookups) == 1:
			mod = __import__(lookups[0].__module__)
			class_ = getattr(mod, lookups[0].__class__.__name__)
			return class_(newWith) if newWith else class_()
		else:
			return lookups
