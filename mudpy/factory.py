from utility import *
from race import *
from ability import *
from command import *

class Factory:
	@staticmethod
	def new(**kwargs):
		for _type, _class in kwargs.iteritems():
			lookup = startsWith(_class, globals()[_type].__subclasses__());
			if lookup:
				return lookup()
			else:
				raise NameError("Factory cannot create a new instance of: "+_type+"."+_class)
