from utility import *
from race import *
from ability import *
from command import *
from room import *

class Factory:
	@staticmethod
	def new(**kwargs):
		lookups = []
		for _type, _class in kwargs.iteritems():
			lookup = startsWith(_class, globals()[_type].__subclasses__());
			if lookup:
				lookups.append(lookup())
			else:
				raise NameError("Factory cannot create a new instance of: "+_type+"."+_class)
		if len(lookups) == 1: #scalar
			mod = __import__(lookups[0].__module__)
			class_ = getattr(mod, lookups[0].__class__.__name__)
			return class_()
		else:
			return lookups
