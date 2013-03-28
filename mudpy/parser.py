from assign import *
from mudpy.debug import Debug
from mudpy.ability import Ability
from mudpy.affect import Affect
from mudpy.proficiency import Proficiency
from mudpy.race import Race
from mudpy.room import Room, Randomhall, Grid, Area
from mudpy.actor import Mob
from mudpy.item import Item, Drink

import os, json

class Parser(object):
	BASEPATH = 'mudpy'
	_globals = []

	def parseDir(self, path):
		Debug.log('parsing scripts for '+path)
		for infile in os.listdir(path):
			fullpath = path+'/'+infile
			if os.path.isdir(fullpath):
				# recurse through scripts directory tree
				self.parseDir(fullpath)
			elif fullpath.endswith('.json'):
				self.parseJson(fullpath)
	
	def parseJson(self, scriptFile):
		Debug.log('parsing json script file: '+scriptFile)
		fp = open(scriptFile)
		data = json.load(fp)
		self._parseJson(None, data)
	
	def _parseJson(self, parent, data):
		from mudpy.factory import Factory
		for item in data:
			for _class in item:
				_class = str(_class)
				instance = globals()[_class]()
				for descriptor in item[_class]:
					if descriptor == 'properties':
						for prop in item[_class][descriptor]:
							setattr(instance, prop, self.guessType(item[_class][descriptor][prop]))
					elif descriptor == 'affects':
						for affect in item[_class][descriptor]:
							instance.affects.append(Factory.new(Affect=affect))
					elif descriptor == "attributes":
						for attribute in item[_class][descriptor]:
							setattr(instance.attributes, attribute, self.guessType(item[_class][descriptor][attribute]))
					elif descriptor == "proficiencies":
						for prof, level in item[_class][descriptor].iteritems():
							instance.addProficiency(prof, level)
					elif descriptor == "mobs" or descriptor == "inventory":
						self.parseJsonObject(instance, item[_class][descriptor])
				getattr(self, 'doneParse'+_class)(parent, instance)
	
	def doneParseAffect(self, parent, affect):
		Parser._globals.append(affect)

	def doneParseRace(self, parent, race):
		Parser._globals.append(race)

	@staticmethod
	def parse(path):
		p = Parser()
		p.parseDir(Parser.BASEPATH+'/'+path)

	@staticmethod
	def guessType(value):
		try:
			if value.isdigit():
				return int(value)
			try:
				return float(value)
			except ValueError: pass
		except AttributeError: pass
		if value == "True":
			return True
		if value == "False":
			return False
		return value
	
class ParserException(Exception): pass
