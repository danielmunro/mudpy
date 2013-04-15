from utility import startsWith
from race import Race
from ability import Ability
from room import *
from command import *
from proficiency import Proficiency
from affect import Affect
import copy, inspect

class Factory:
	wireframes = {}

	@staticmethod
	def new(scalar = True, newWith = None, **kwargs):
		from parser import Parser
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

	@staticmethod
	def newFromWireframe(scalar = True, **kwargs):
		instances = []
		from parser import Parser
		p = Parser()
		for key, name in kwargs.iteritems():
			try:
				wireframes = Factory.wireframes[key][name]
			except KeyError:
				raise FactoryException("Wireframe not defined: "+key)
			instances = instances + p._parseJson(wireframes)
		return instances[0] if scalar else instances

	@staticmethod
	def addWireframes(wireframes):
		for wireframe in wireframes:
			for key, blob in wireframe.iteritems():
				name = blob['properties']['name']
				try:
					Factory.wireframes[key][name] = [wireframe]
				except KeyError:
					Factory.wireframes[key] = {}
					Factory.wireframes[key][name] = [wireframe]

class FactoryException(Exception): pass
