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
			lookup = startsWith(_class, globals()[_type].__subclasses__())
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
	def newFromWireframe(instance, name):
		try:
			wireframes = Factory.wireframes[instance.__class__.__name__][name]
		except KeyError:
			raise FactoryException("Factory does not know how to create "+name)
		from parser import Parser
		p = Parser()
		return p.buildFromDefinition(instance, wireframes[instance.__class__.__name__])

	@staticmethod
	def addWireframes(wireframes):
		for wireframe in wireframes:
			for key, blob in wireframe.iteritems():
				name = blob['properties']['name']
				try:
					Factory.wireframes[key][name] = wireframe
				except KeyError:
					Factory.wireframes[key] = {}
					Factory.wireframes[key][name] = wireframe
	
	@staticmethod
	def matchWireframe(name, keys, scalar = True):
		matches = []
		if not isinstance(keys, list):
			keys = [keys]
		for key in keys:
			for wireframename, wireframe in Factory.wireframes[key].iteritems():
				if wireframename.startswith(name):
					matches.append({'key':key, 'wireframe':wireframename})
		try:
			return matches[0] if scalar else matches
		except KeyError:
			return None

class FactoryException(Exception): pass
